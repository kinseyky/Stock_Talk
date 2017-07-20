import logging
import os

from flask import Flask
from flask_ask import Ask, request, session, question, statement
import requests, bs4

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

@ask.launch
def launch():
    speech_text = "Want to talk Stocks?"
    return question(speech_text).simple_card('Stock Talk', speech_text)

def stock_symbol_from_name(StockSymbol):
    #query google finance
    page_request = requests.get('https://www.google.com/finance?q={}'.format(StockSymbol))

    page = bs4.BeautifulSoup(page_request.text)

    #using the page metadata, grab the symbol and exchange
    symbol = page.find("meta", {"itemprop": "tickerSymbol"})['content']
    exchange = page.find("meta", {"itemprop": "exchange"})['content']

    return symbol, exchange

def build_response_string(symbol, exchange, company_name):
    return "{} trades on the {} under the symbol {}.".format(company_name, exchange, symbol)

#remove extraneous characters and make the string friendly to send to a request
def sanitize_input(company_name):
    company_name = company_name.lower().replace("the", "").replace(" ", "_")
    return company_name

@ask.intent('GetStockSymbol')
def get_stock_price(company_name):
    company_name_clean = sanitize_input(company_name)
    symbol, exchange = stock_symbol_from_name(company_name_clean)
    speech_text = build_response_string(symbol, exchange, company_name)
    return statement(speech_text).simple_card('Stock Talk', speech_text)


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)