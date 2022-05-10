import os
import json
import requests

from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder


@csrf_exempt
def nested_call_handler(request):
    if request.method == 'POST':
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
                    message["actions"][i]["statPus"] = "Passed"
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
                if resp is None:
                    errors.append("failed to call service " + action["payload"]["serviceName"])
                    message["actions"][i]["status"] = "Failed"
                else:
                    message["actions"][i]["statPus"] = "Passed"
                    message["actions"][i]["payload"]["actions"] = resp["actions"]

            message["actions"][i]["serviceName"] = "backend-python-django"
            message["actions"][i]["returnTime"] = datetime.utcnow()

        message["meta"]["returnTime"] = datetime.utcnow()

        response = json.dumps(message, cls=DjangoJSONEncoder)

        log_context(request, response, errors, received_at)

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
    suffix = os.environ["SANDBOX_ENDPOINT_DNS_SUFFIX"] + "/api"
    if serviceName == "backend-go-gin":
        return "https://gin" + suffix
    if serviceName == "backend-typescript-express":
        return "https://express" + suffix
    if serviceName == "backend-ruby-rails":
        return "https://rails" + suffix
    if serviceName == "backend-kotlin-spring":
        return "https://spring" + suffix
    if serviceName == "backend-python-django":
        return "https://django" + suffix
    else:
        return "unknown"


def read_entity(store, key):
    return {"value": None, "errors": store + " client not implemented yet"}


def write_entity(store, key, value):
    return {"value": value, "errors": store + " client not implemented yet"}


def log_context(request, response, errors, received_at):
    print("Started POST \"/api\" at " + str(received_at), flush=True)
    print("  Request: " + request, flush=True)
    print("  Response: " + response, flush=True)
    if len(errors) > 0:
        print("  Errors: " + ", ".join(errors), flush=True)
    print("\n", flush=True)
