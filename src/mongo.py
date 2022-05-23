from os import environ
from pymongo import MongoClient


def mongo_client():
    HOST = environ.get('MONGODB_SERVICE_HOST')
    PORT = int(environ.get('MONGODB_SERVICE_PORT'))

    client = MongoClient(host=HOST, port=PORT)

    return client.demo
