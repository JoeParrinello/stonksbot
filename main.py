"""StonksBot CloudFunction."""
import os
import re
import threading
import finnhub_api
from flask import jsonify
import functions_framework
import requests
from google.cloud import secretmanager
from discord_types import ApplicationCommandType, ApplicationCommandOptionType, InteractionType, InteractionCallbackType


project_id = os.environ["PROJECT_ID"]
stonksbot_app_id = os.environ["DISCORD_APPLICATION_ID"]

client = secretmanager.SecretManagerServiceClient()
discord_token_name = f"projects/{project_id}/secrets/stonksbot_discord_token/versions/latest"
discord_token_response = client.access_secret_version(name=discord_token_name)
discord_token = discord_token_response.payload.data.decode("UTF-8")


def construct_patch_url(response_token):
    return f"https://discord.com/api/webhooks/{stonksbot_app_id}/{response_token}/messages/@original"


def normalize_stock_ticker(unnormalized_string):
    """Takes a stock ticker string, and returns the normalized string.

    Returns None if there is an error.
    """
    match = re.fullmatch("[A-Za-z]{1,5}", unnormalized_string)
    if match is None:
        return None

    return unnormalized_string.upper()


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
        response_token = request_json["token"]
        if 'data' in request_json:
            command_data = request_json['data']
            if command_data['type'] == ApplicationCommandType.CHAT_INPUT and command_data['name'] == "stonks":
                stock_string = command_data["options"][0]["value"]
                stock_string = normalize_stock_ticker(stock_string)
                if stock_string is not None:
                    thread = threading.Thread(target=run_quote_thread, args=(response_token, stock_string))
                    thread.start()
                    return jsonify({
                    "type": InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": "Fetching stock price"}
                })
                return jsonify({
                    "type": InteractionCallbackType.CHANNEL_MESSAGE_WITH_SOURCE,
                    "data": {"content": "Invalid Stock Ticker"}
                })

    return "Success", 200


def run_quote_thread(response_token, stock_ticker):
    quote = finnhub_api.get_stock_quote(stock_ticker)
    json = {
        "content": "Stock Ticker Fetch Failed",
    }
    if quote is not None:
        json = {
            "embeds": [quote.embeddable_message()],
        }
    
    headers = {
        "Authorization": f"Bot {discord_token}"
    }
    requests.patch(construct_patch_url(response_token), headers=headers, json=json, timeout=30)


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
