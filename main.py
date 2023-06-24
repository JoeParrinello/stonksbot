"""StonksBot CloudFunction."""
import os
import re
from flask import jsonify, Flask
from discord_interactions import (
    ApplicationCommand,
    ApplicationCommandOption,
    ApplicationCommandOptionType,
    Interaction,
    InteractionResponse,
    InteractionCallbackType,
    InteractionApplicationCommandCallbackData,
)
from google.cloud import secretmanager
from discord_interactions.flask_ext import (AfterCommandContext, Interactions,)


project_id = os.environ["PROJECT_ID"]
stonksbot_app_id = os.environ["DISCORD_APPLICATION_ID"]

client = secretmanager.SecretManagerServiceClient()
discord_token_name = f"projects/{project_id}/secrets/stonksbot_discord_token/versions/latest"
discord_token_response = client.access_secret_version(name=discord_token_name)
discord_token = discord_token_response.payload.data.decode("UTF-8")

app = Flask(__name__)
interactions = Interactions(app, discord_token)

stonks_cmd = ApplicationCommand("stonks", "Request the price info on a stock")
stonks_cmd.add_option(
    ApplicationCommandOption(
        type=ApplicationCommandOptionType.STRING,
        name="ticker",
        description="This will be the stock checked for its value.",
        required=True,
    )
)


@interactions.command(stonks_cmd)
def _stonks(interaction: Interaction):
    return InteractionResponse(
        type=InteractionCallbackType.DEFERRED_CHANNEL_MESSAGE,
        data=InteractionApplicationCommandCallbackData(content="Fetching stock price."),
    )

@_stonks.after_command
def _after_stonks_response(ctx: AfterCommandContext):
    stock_ticker = ctx.interaction.data.options[0].value
    ctx.send(f"{stock_ticker} recieved")
