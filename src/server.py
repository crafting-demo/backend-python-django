import json
import requests

from os import environ
from datetime import datetime
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder

@csrf_exempt
def api_call_handler(request):
    if request.method == 'POST':

        received_at = datetime.utcnow()
        message = json.loads(request.body)
        print("\n\nReceived API message " + message["message"] + " at " + str(received_at), flush=True)

        if message["message"] == "Hello! How are you?":
            response = "Hello! This is Python Django service."
        elif message["message"] == "Please echo":
            response = "Echo from Python Django service: " + message["value"]
        elif message["message"] == "Read from database":
            value = read_entity("mysql", message["key"])
            if (value is None):
                print("Not found key " + message["key"], flush=True)
            else:
                response = "Python Django service: successfully read from database, value: " + value
        elif message["message"] == "Write to database":
            write_entity("mysql", message["key"], message["value"])
            response = "Python Django service: successfully write to database"

        return_at = datetime.utcnow()

        print("Finished processing API message " + message["message"] + " at " + str(return_at), flush=True)

        res = {
            "receivedTime": received_at,
            "returnTime": return_at,
            "message": response,
        }

        return JsonResponse(res)

def read_entity(store, key):
    if store == "mysql":
        with connection.cursor() as cursor:
            stmt = "select content from sample where uuid='" + key + "'"
            cursor.execute(stmt)
            if cursor.rowcount == 0:
                value = None
            else:
                value = cursor.fetchone()[0]
            return value
    return None


def write_entity(store, key, value):
    if store == "mysql":
        with connection.cursor() as cursor:
            stmt = "insert into sample (uuid, content) values (%s, %s) ON DUPLICATE KEY UPDATE content = %s"
            cursor.execute(stmt, (key, value, value))

