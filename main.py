import requests
import smtplib, ssl
import os
import selectorlib
import time
import sqlite3

URL = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}



class Event:
    def scrape(self, url):
        """Scrape page source from URL"""
        response = requests.get(url, headers=HEADERS)
        source = response.text
        return source

    def extract(self, source):
        extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
        value = extractor.extract(source)['tours']
        return value


class Email:

    def send(self, message):

        host = "smtp.gmail.com"
        port = 456

        username = '#Email address'
        password = '#Gmail password'

        receiver = '#Send to Email'
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(host, port, context=context) as server:
            server.login(username, password)
            server.sendmail(username, receiver, message)

class Database:
    def __init__(self, database_path):
        self.connections = sqlite3.connect(database_path)

    def store(self, extracted):
        row = extracted.split(",")
        row = [item.strip() for item in row]
        cursor = self.connections.cursor()
        cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
        #Execute into SQL
        self.connections.commit()

    def read_file(self, extracted):
        row = extracted.split(",")
        row = [item.strip() for item in row]
        band, city, date = row

        #SQL connection
        cursor = self.connections.cursor()
        cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
        rows = cursor.fetchall()
        return rows


if __name__ == "__main__":
    while True:
        #Call Event class
        event = Event()
        scraped = event.scrape(URL)
        extracted = event.extract(scraped)

        if extracted != "No upcoming tours":
            database = Database("data.db")
            row = database.read_file(extracted)

            #If no such rows, store new data
            if not row:
                #Store event if new
                database.store(extracted)
                email = Email()
                email.send("New event was found")

        time.sleep(2)
