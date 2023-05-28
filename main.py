"""StonksBot CloudFunction."""
import os
from flask import jsonify
import functions_framework
import requests
from google.cloud import secretmanager
from discord_types import ApplicationCommandType, ApplicationCommandOptionType, InteractionType, InteractionCallbackType


project_id = os.environ["PROJECT_ID"]
client = secretmanager.SecretManagerServiceClient()
name = f"projects/{project_id}/secrets/stonksbot_app_id/versions/latest"
response = client.access_secret_version(name=name)
stonksbot_app_id = response.payload.data.decode("UTF-8")

discord_token_name = f"projects/{project_id}/secrets/stonksbot_discord_token/versions/latest"
discord_token_response = client.access_secret_version(name=discord_token_name)
discord_token = discord_token_response.payload.data.decode("UTF-8")

@functions_framework.http
def discord_webhook(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    if request_json is None or 'type' not in request_json:
        return "Failed to parse json", 500

    if request_json["type"] == InteractionType.PING:
        return jsonify({
            "type": InteractionCallbackType.PONG
        })
    
    if request_json["type"] == InteractionType.APPLICATION_COMMAND:
        if 'data' in request_json:
            command_data = request_json['data']
            if command_data['type'] == ApplicationCommandType.CHAT_INPUT and command_data['name'] == "stonks":
                stock_string = command_data["options"][0]["value"]
                return jsonify({
                    "type": InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": f"I recieved {stock_string}"}
                })


    return "Success", 200

@functions_framework.http
def register_bot(request):
    """HTTP Cloud Function
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    url = f"https://discord.com/api/v10/applications/{stonksbot_app_id}/commands"

    json = {
        "name": "stonks",
        "type": ApplicationCommandType.CHAT_INPUT,
        "description": "Request the price info on a stock",
        "options": [
            {
                "name": "ticker",
                "description": "The stock ticker as listed on the market.",
                "type": ApplicationCommandOptionType.STRING,
                "required": True,
            }
        ]
    }
    headers = {
        "Authorization": f"Bot {discord_token}"
    }
    requests.post(url, headers=headers, json=json, timeout=30)
    return "Success", 200
