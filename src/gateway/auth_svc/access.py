import os
import requests

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)

    response = requests.post(
        f"http://{os.getenv('AUTH_SVC_ADDRESS')}/login",
        auth=(auth.username, auth.password)
    )

    if response.status_code == 200:
        return response.text, None
    return None, (response.text, response.status_code)
