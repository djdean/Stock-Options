import requests
import json
from authlib.integrations.requests_client import OAuth1Session
import webbrowser

class Config:
    def __init__(self, config_path):
        self.config_path = config_path
    def read_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)

class Broker():
    def __init__(self, config_path, name):
        self.config_path = config_path
        self.name = name

    def get_options_data(self, symbol):
        pass

    def get_quotes(self, symbol,Sandbox=True):
        pass

    def authorize(self):
        pass
 
    def check_config(self):
        pass
class Polygon_IO(Broker):
    def __init__(self, config_path, name):
        self.name = name
        self.config_options = Config(config_path)
        self.config_data = self.config_options.read_config()
    def get_options_data(self, symbol):
        url = self.config_data.get('polygon_options_url') + symbol + '/options'
        print(url)
        response = requests.get(url)
        return response.text
    def get_quotes(self, symbol):
        url = self.config_data.get('polygon_quote_url') + symbol
        print(url)
        response = requests.get(url)
        return response.text
    def check_config(self):
        if self.config_data.get('polygon_options_url') is None or self.config_data.get('polygon_options_url') == '' \
            or self.config_data.get('polygon_quote_url') is None or self.config_data.get('polygon_quote_url') == '':
            return False
        else:
            return True
        
class E_trade (Broker):

    def __init__(self, config_path, name):
        self.name = name
        self.config_options = Config(config_path)
        self.config_data = self.config_options.read_config()
        self.prod = self.config_data.get('prod')
        self.config_consumer_key=self.config_data.get('e_trade_sb_oauth_consumer_key')
        self.config_consumer_secret=self.config_data.get('e_trade_sb_oauth_consumer_secret')
        if self.prod:
            self.config_consumer_key=self.config_data.get('e_trade_prod_oauth_consumer_key')
            self.config_consumer_secret=self.config_data.get('e_trade_prod_oauth_consumer_secret')
        self.options_url = self.config_data.get('sb_options_url')
        self.quotes_url = self.config_data.get('sb_quote_url')
        if self.prod:
            self.options_url = self.config_data.get('prod_options_url')
            self.quotes_url = self.config_data.get('prod_quote_url')
    
    def create_authlib_session(self) -> OAuth1Session:  
        client = OAuth1Session(self.config_consumer_key, self.config_consumer_secret)
        return client

    def authorize(self):
        print("Authorizing Application...")      
        self.session = self.create_authlib_session()
        self.session.redirect_uri = 'oob'
        request_token = self.session.fetch_request_token(self.config_data.get('request_token_url'))
        print("E-Trade OAuth Request Token: " + str(request_token['oauth_token']))
        authorization_url = self.config_data.get('authorize_url').format( self.config_consumer_key, request_token['oauth_token'])        
        print("E-Trade OAuth Authorize URL: " + authorization_url)
        print("E-Trade Request Token: " + str(request_token))
        webbrowser.open(authorization_url)
        text_code = input("Please accept agreement and enter verification code from browser: ")
        access_token = self.session.fetch_access_token(self.config_data.get('access_token_url'), verifier=text_code)
        print("E-Trade OAuth Access Token: " + str(access_token))
        return True

    def get_quotes(self, symbol):
        quotes_url = self.quotes_url + "/" + symbol
        print(quotes_url)
        response = self.session.get(quotes_url)
        return response.text

    def get_options_data(self, symbol):     
        options_url = self.options_url + "?symbol=" + symbol
        print(options_url)
        response = self.session.get(options_url)
        return response.text
    
    def check_config(self):
        if self.config_data.get('e_trade_sb_oauth_consumer_key') is None or self.config_data.get('e_trade_sb_oauth_consumer_key') == '' \
            or self.config_data.get('e_trade_sb_oauth_consumer_secret') is None or self.config_data.get('e_trade_sb_oauth_consumer_secret') == '' \
            or self.config_data.get('e_trade_prod_oauth_consumer_key') is None or self.config_data.get('e_trade_prod_oauth_consumer_key') == '' \
            or self.config_data.get('e_trade_prod_oauth_consumer_secret') is None or self.config_data.get('e_trade_prod_oauth_consumer_secret') == '' \
            or self.config_data.get('request_token_url') is None  or self.config_data.get('request_token_url') == '' \
            or self.config_data.get('access_token_url') is None or self.config_data.get('access_token_url') == '' \
            or self.config_data.get('authorize_url') is None or self.config_data.get('authorize_url')== '' \
            or self.config_data.get('prod') is None or self.config_data.get('prod')== '' \
            or self.config_data.get('prod_options_url') is None or self.config_data.get('prod_options_url')== '' \
            or self.config_data.get('prod_quote_url') is None or self.config_data.get('prod_quote_url')== '' \
            or self.config_data.get('prod_base_url') is None or self.config_data.get('prod_base_url') == '' \
            or self.config_data.get('sb_options_url') is None or self.config_data.get('sb_options_url')== '' \
            or self.config_data.get('sb_quote_url') is None or self.config_data.get('sb_quote_url')== '' \
            or self.config_data.get('sb_base_url') is None or self.config_data.get('sb_base_url') == '':
            return False
        else:
            return True
        
def init_brokers() -> list[Broker]:
    brokers = []
    brokers.append(E_trade("./local_config/e_trade_config.json","etrade"))
    return brokers

def main():
    brokers = init_brokers()
    for broker in brokers:
        if not broker.check_config():
            print(broker.name + " config file is missing required parameters")
            return
        print("Authorizing " + broker.name + "...")
        broker.authorize()
        print("Getting options data for JPM...")
        print(broker.get_options_data('JPM'))
        print("Getting quotes for JPM...")
        print(broker.get_quotes('JPM'))

if __name__ == '__main__':
    main()
   
