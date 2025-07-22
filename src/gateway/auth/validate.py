import os
import requests

def token(request):
    token = request.headers.get("Authorization")
    if not token:
        return None, ("missing token", 401)

    response = requests.post(
        f"http://{os.getenv('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token}
    )

    if response.status_code == 200:
        return response.text, None
    return None, (response.text, response.status_code)
