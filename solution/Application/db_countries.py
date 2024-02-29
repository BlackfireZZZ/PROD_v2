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

    def get_countries(self, request: Flask.request_class):
        DB_username, DB_password, DB_host, DB_port, DB_name = get_db_params()
        try:
            conn = psycopg2.connect(dbname=DB_name, user=DB_username, password=DB_password, host=DB_host)

            region_param = request.args.get('region')
            if region_param is None:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM countries")
                rows = cursor.fetchall()
                cursor.close()
                conn.close()
                return jsonify(rows), 200
            else:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM countries WHERE region = %s", (region_param,))
                rows = cursor.fetchall()
                return jsonify(rows), 200
        except:
            return jsonify({"status": "Cannot connect to database"}), 500




