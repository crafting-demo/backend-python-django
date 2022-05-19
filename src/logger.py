def log_context(request, response, errors, received_at):
    print("Started POST \"/api\" at " + str(received_at), flush=True)
    print("  Request: " + request, flush=True)
    print("  Response: " + response, flush=True)
    if len(errors) > 0:
        print("  Errors: " + ", ".join(errors), flush=True)
    print("\n", flush=True)
