"""Finnhub client integration."""
import os
import finnhub
from finnhub.exceptions import FinnhubAPIException
from finnhub.exceptions import FinnhubRequestException
from google.cloud import secretmanager

project_id = os.environ["PROJECT_ID"]
client = secretmanager.SecretManagerServiceClient()
name = f"projects/{project_id}/secrets/finnhub_token/versions/latest"
response = client.access_secret_version(name=name)
finnhub_token = response.payload.data.decode("UTF-8")
finnhub_client = finnhub.Client(api_key=finnhub_token)


class TickerQuote:
    """Represents a single Ticker request.
    """

    def __init__(self, ticker, price, previous_close, company_name=None):
        self._ticker = ticker
        self._price = price
        self._previous_close = previous_close
        self._company_name = company_name

    def _get_percent_change(self):
        return ((self._price - self._previous_close) / self._previous_close) * 100

    def _get_title(self):
        if self._company_name is None:
            return self._ticker
        return f"{self._company_name} ({self._ticker})"

    def embeddable_message(self):
        """
        Returns the embeddable message to return to discord.
        """
        return {'title': self._get_title(),
                'description': f"{self._price} ({self._get_percent_change()}%)",
                'type': 'rich'
                }


def get_stock_quote(ticker):
    """
    Returns the quote for a given Ticker, or None if not valid.
    """
    try:
        quote = finnhub_client.quote(ticker)
        if quote['c'] == 0.0:
            return None
        company = finnhub_client.company_profile2(symbol=ticker)
        if 'name' in company:
            return TickerQuote(ticker, quote['c'], quote['pc'], company['name'])
        return TickerQuote(ticker, quote['c'], quote['pc'])

    except (FinnhubAPIException, FinnhubRequestException) as error:
        print(error)
        return None
