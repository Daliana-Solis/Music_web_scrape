import requests
import smtplib, ssl
import os
import selectorlib
import time
import sqlite3

URL = "https://programmer100.pythonanywhere.com/tours/"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


connections = sqlite3.connect("data.db")


def scrape(url):
    """Scrape page source from URL"""
    response = requests.get(url, headers=HEADERS)
    source = response.text
    return source


def extract(source):
    extractor = selectorlib.Extractor.from_yaml_file("extract.yaml")
    value = extractor.extract(source)['tours']
    return value


def send_email(message):

    host = "smtp.gmail.com"
    port = 456

    username = '#Email address'
    password = '#Gmail password'

    receiver = '#Send to Email'
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)

    print('email sent')


def store(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    cursor = connections.cursor()
    cursor.execute("INSERT INTO events VALUES(?,?,?)", row)
    #Execute into SQL
    connections.commit()


def read_file(extracted):
    row = extracted.split(",")
    row = [item.strip() for item in row]
    band, city, date = row

    #SQL connection
    cursor = connections.cursor()
    cursor.execute("SELECT * FROM events WHERE band=? AND city=? AND date=?", (band, city, date))
    rows = cursor.fetchall()
    return rows


if __name__ == "__main__":
    while True:
        scraped = scrape(URL)
        extracted = extract(scraped)

        if extracted != "No upcoming tours":
            row = read_file(extracted)

            #If no such rows, store new data
            if not row:
                #Store event if new
                store(extracted)
                send_email("New event was found")

        time.sleep(2)
