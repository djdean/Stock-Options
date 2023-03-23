import requests
import json
from rauth import OAuth1Service
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

    def create_service_wrapper(self,prod=False) -> OAuth1Service:
        config_consumer_key=self.config_data.get('e_trade_sb_oauth_consumer_key')
        config_consumer_secret=self.config_data.get('e_trade_sb_oauth_consumer_secret')
        if prod:
            config_consumer_key=self.config_data.get('e_trade_prod_oauth_consumer_key')
            config_consumer_secret=self.config_data.get('e_trade_prod_oauth_consumer_secret')
        service_oauth_wrapper = OAuth1Service(
            name=self.name,
            consumer_key=config_consumer_key,
            consumer_secret=config_consumer_secret,
            request_token_url=self.config_data.get('request_token_url'),
            access_token_url=self.config_data.get('access_token_url'),
            authorize_url=self.config_data.get('authorize_url'),
            base_url=self.config_data.get('sb_base_url'))
        return service_oauth_wrapper

    def authorize(self):
        print("Authorizing Application...")
        prod = False
        if self.config_data.get('prod') == 'True':
            prod = True
        self.service_wrapper = self.create_service_wrapper(prod)
        request_token, request_token_secret =  self.service_wrapper.get_request_token(
            params={"oauth_callback": "oob", "format": "json"})
        print("E-Trade OAuth Request Token: " + str(request_token))
        authorize_url =  self.service_wrapper.authorize_url.format( self.service_wrapper.consumer_key, request_token)
        print("E-Trade OAuth Authorize URL: " + authorize_url)
        print("E-Trade OAuth Request Token Secret: " + str(request_token_secret))
        print("E-Trade Request Token: " + str(request_token))
        webbrowser.open(authorize_url)
        text_code = input("Please accept agreement and enter verification code from browser: ")
        self.session =  self.service_wrapper.get_auth_session(request_token,
                                  request_token_secret,
                                  params={"oauth_verifier": text_code})
        return True

    def get_quotes(self, symbol):
        prod = self.config_data.get('prod')
        url = self.config_data.get('sb_quote_url') + "/" + symbol
        if prod:
            url = self.config_data.get('prod_quote_url') + "/" + symbol
        print(url)
        response = self.session.get(url, header_auth=False)
        return response.text

    def get_options_data(self, symbol):
        prod = self.config_data.get('prod')
        url = self.config_data.get('sb_options_url') + "/" + symbol
        if prod:
            url = self.config_data.get('prod_options_url') + "/" + symbol
        response = self.session.get(url, header_auth=False, params={"symbol": symbol})
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
   
