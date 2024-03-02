import os
import psycopg2
from flask import Flask, jsonify


def get_db_params():
    DB_username = os.environ.get('POSTGRES_USERNAME')
    DB_password = os.environ.get('POSTGRES_PASSWORD')
    DB_host = os.environ.get('POSTGRES_HOST')
    DB_port = os.environ.get('POSTGRES_PORT')
    DB_name = os.environ.get('POSTGRES_DATABASE')
    return DB_username, DB_password, DB_host, DB_port, DB_name


class Countries:
    def __init__(self):
        self.conn = psycopg2.connect(dbname=os.environ.get('POSTGRES_DATABASE'),
                                     user=os.environ.get('POSTGRES_USERNAME'),
                                     password=os.environ.get('POSTGRES_PASSWORD'),
                                     host=os.environ.get('POSTGRES_HOST'),
                                     port=os.environ.get('POSTGRES_PORT'))

    @staticmethod
    def get_countries(region=None):
        DB_username, DB_password, DB_host, DB_port, DB_name = get_db_params()
        try:
            conn = psycopg2.connect(dbname=DB_name, user=DB_username, password=DB_password, host=DB_host)
            if region is None:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM countries")
                rows = cursor.fetchall()
                cursor.close()
                conn.close()
                return rows
            else:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM countries WHERE region = %s", (region,))
                rows = cursor.fetchall()
                return rows
        except:
            return "Cannot connect to database"

    @staticmethod
    def get_country(code):
        DB_username, DB_password, DB_host, DB_port, DB_name = get_db_params()
        try:
            conn = psycopg2.connect(dbname=DB_name, user=DB_username, password=DB_password, host=DB_host)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM countries WHERE %s = alpha2', (code,))
            row = cursor.fetchone()
            if row is None:
                return 'Country not found'
            cursor.close()
            conn.close()
            return row
        except:
            return 'Cannot connect to database'

    @staticmethod
    def check_country_code(countryCode):  # check if country code is correct
        if countryCode is None:
            return 'Country code is empty', 400
        if len(countryCode) > 2:
            return 'Country code is too long', 400
        if len(countryCode) < 2:
            return 'Country code is too short', 400
        rows = Countries.get_country(countryCode)
        if rows is None:
            return 'Country code is incorrect', 400
        else:
            return 'OK', 200

