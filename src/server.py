import json
import requests

from os import environ
from datetime import datetime
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder

from . import mongo
from . import logger


@csrf_exempt
def nested_call_handler(request):
    if request.method == 'POST':
        # logger.write("Test Test Crafting")

        received_at = datetime.utcnow()
        errors = []

        message = json.loads(request.body)

        request = json.dumps(message, cls=DjangoJSONEncoder)

        for i, action in enumerate(message["actions"]):
            if action["action"] == "Echo":
                message["actions"][i]["status"] = "Passed"
            elif action["action"] == "Read":
                res = read_entity(
                    action["payload"]["serviceName"],
                    action["payload"]["key"])
                if res["errors"] is not None:
                    errors.append(res["errors"])
                    message["actions"][i]["status"] = "Failed"
                else:
                    message["actions"][i]["status"] = "Passed"
                    message["actions"][i]["payload"]["value"] = res["value"]
            elif action["action"] == "Write":
                res = write_entity(
                    action["payload"]["serviceName"],
                    action["payload"]["key"],
                    action["payload"]["value"])
                if res["errors"] is not None:
                    errors.append(res["errors"])
                    message["actions"][i]["status"] = "Failed"
                else:
                    message["actions"][i]["status"] = "Passed"
            elif action["action"] == "Call":
                resp = service_call(action["payload"])
                if resp is None or 'error' in resp:
                    errors.append("failed to call service " + action["payload"]["serviceName"])
                    message["actions"][i]["status"] = "Failed"
                else:
                    message["actions"][i]["status"] = "Passed"
                    message["actions"][i]["payload"]["actions"] = resp["actions"]

            message["actions"][i]["serviceName"] = "backend-python-django"
            message["actions"][i]["returnTime"] = datetime.utcnow()

        message["meta"]["returnTime"] = datetime.utcnow()

        response = json.dumps(message, cls=DjangoJSONEncoder)

        logger.log_context(request, response, errors, received_at)

        return JsonResponse(message)


def service_call(payload):
    message = {
        "meta": {
            "caller": "backend-python-django",
            "callee": payload["serviceName"],
            "callTime": datetime.utcnow()
        },
        "actions": payload["actions"]
    }
    data = json.dumps(message, cls=DjangoJSONEncoder)
    response = requests.post(service_endpoint(
        payload["serviceName"]), json=json.loads(data))
    return json.loads(response.content)


def service_endpoint(serviceName):
    host = ""
    port = ""
    if serviceName == "backend-go-gin":
        host = environ.get("GIN_SERVICE_HOST")
        port = environ.get("GIN_SERVICE_PORT")
    if serviceName == "backend-typescript-express":
        host = environ.get("EXPRESS_SERVICE_HOST")
        port = environ.get("EXPRESS_SERVICE_PORT")
    if serviceName == "backend-ruby-rails":
        host = environ.get("RAILS_SERVICE_HOST")
        port = environ.get("RAILS_SERVICE_PORT")
    if serviceName == "backend-kotlin-spring":
        host = environ.get("SPRING_SERVICE_HOST")
        port = environ.get("SPRING_SERVICE_PORT")
    if serviceName == "backend-python-django":
        host = environ.get("DJANGO_SERVICE_HOST")
        port = environ.get("DJANGO_SERVICE_PORT")
    return "http://" + host + ":" + port + "/api"


def read_entity(store, key):
    if store == "mysql":
        return read_mysql(key)
    if store == "mongodb":
        return read_mongodb(key)
    else:
        return {"value": None, "errors": store + " not supported"}


def write_entity(store, key, value):
    if store == "mysql":
        return write_mysql(key, value)
    if store == "mongodb":
        return write_mongodb(key, value)
    else:
        return {"value": None, "errors": store + " not supported"}


def read_mysql(key):
    with connection.cursor() as cursor:
        stmt = "select content from sample where uuid='" + key + "'"
        cursor.execute(stmt)
        if cursor.rowcount == 0:
            value = "Not Found"
        else:
            value = cursor.fetchone()[0]
        return {"value": value, "errors": None}


def write_mysql(key, value):
    with connection.cursor() as cursor:
        stmt = "insert into sample (uuid, content) values (%s, %s)"
        cursor.execute(stmt, (key, value))
        return {"value": value, "errors": None}


def read_mongodb(key):
    conn = db.mongo_client()
    result = conn.sample.find_one({"uuid": key})
    if result is None:
        value = "Not Found"
    else:
        value = result["content"]
    return {"value": value, "errors": None}


def write_mongodb(key, value):
    conn = db.mongo_client()
    conn.sample.insert_one({"uuid": key, "content": value})
    return {"value": value, "errors": None}
