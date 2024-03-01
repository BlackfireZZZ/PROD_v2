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





