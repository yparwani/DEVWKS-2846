import os
import requests

def get_oauth_token():
    url = "https://id.cisco.com/oauth2/default/v1/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': '',
        'client_secret': ''
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()  # Raise an error for bad responses

    return response.json()['access_token']