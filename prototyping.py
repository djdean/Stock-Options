import requests
import json
from authlib.integrations.requests_client import OAuth1Session
import webbrowser

class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config_data = self.read_config()
    def read_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)
    def check_config(self):
        pass

class AppConfig(Config):
    def __init__(self, config_path):     
        super().__init__(config_path)

    def check_config(self):
        if self.config_data.get('mode') is None or self.config_data.get('mode') == '' \
        or self.config_data.get('local_config_path') is None or self.config_data.get('local_config_path') == '':
            return False
        return True   
        
class ETradeConfig(Config):
     def __init__(self, config_path):
        super().__init__(config_path)
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
        
class Broker():
    def __init__(self, config_path, name):
        pass

    def get_options_data(self, symbol):
        pass

    def get_quotes(self, symbol):
        pass

    def authorize(self):
        pass
 
    def check_config(self):
        pass

    def run_interactive(self):
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
        try:
            self.name = name
            self.config_options = ETradeConfig(config_path)
            if not self.config_options.check_config():
                raise ValueError('ETradeConfig is missing required values')
            self.prod = self.config_options.config_data.get('prod')
            self.config_consumer_key=self.config_options.config_data.get('e_trade_sb_oauth_consumer_key')
            self.config_consumer_secret=self.config_options.config_data.get('e_trade_sb_oauth_consumer_secret')
            if self.prod:
                self.config_consumer_key=self.config_options.config_data.get('e_trade_prod_oauth_consumer_key')
                self.config_consumer_secret=self.config_options.config_data.get('e_trade_prod_oauth_consumer_secret')
            self.options_url = self.config_options.config_data.get('sb_options_url')
            self.quotes_url = self.config_options.config_data.get('sb_quote_url')
            if self.prod:
                self.options_url = self.config_options.config_data.get('prod_options_url')
                self.quotes_url = self.config_options.config_data.get('prod_quote_url')
        except IOError:
            print("Error reading config file: " + config_path)
            return None
        except ValueError as e:
            print(str(e))
            return None
    
    def create_authlib_session(self) -> OAuth1Session:  
        client = OAuth1Session(self.config_consumer_key, self.config_consumer_secret)
        return client

    def authorize(self):
        print("Authorizing Application...")      
        self.session = self.create_authlib_session()
        self.session.redirect_uri = 'oob'
        request_token = self.session.fetch_request_token(self.config_options.config_data.get('request_token_url'))
        print("E-Trade OAuth Request Token: " + str(request_token['oauth_token']))
        authorization_url = self.config_options.config_data.get('authorize_url').format( self.config_consumer_key, request_token['oauth_token'])        
        print("E-Trade OAuth Authorize URL: " + authorization_url)
        print("E-Trade Request Token: " + str(request_token))
        webbrowser.open(authorization_url)
        text_code = input("Please accept agreement and enter verification code from browser: ")
        access_token = self.session.fetch_access_token(self.config_options.config_data.get('access_token_url'), verifier=text_code)
        print("E-Trade OAuth Access Token: " + str(access_token))
        return True

    def get_quotes(self, symbol):
        quotes_url = self.quotes_url + "/" + symbol+".json"
        print(quotes_url)
        response = self.session.get(quotes_url)
        return response.text

    def get_options_data(self, symbol):     
        options_url = self.options_url + "?symbol=" + symbol
        print(options_url)
        response = self.session.get(options_url)
        return response.text
    
    def run_interactive(self):
        while(True):
            print("Using broker: " + self.name)
            print("Options - ")
            print("\t1. Get options chain data")
            print("\t2. Get quotes")
            print("\t3. Exit")
            broker_option = input("Enter selection: ")
            try:
                broker_option = int(broker_option)
                if broker_option == 1:
                    symbol = input("Enter symbol: ")
                    print(self.get_options_data(symbol))
                elif broker_option == 2:
                    symbol = input("Enter symbol: ")
                    print(self.get_quotes(symbol))
                elif broker_option == 3:
                    return 
            except ValueError:
                print("Invalid selection") 
        
def init_brokers(local_config_path) -> list[Broker]:
    brokers = []
    e_trade_broker = E_trade(local_config_path+"/e_trade_config.json","E-Trade")
    if not e_trade_broker == None:
        brokers.append(e_trade_broker)
    return brokers

def list_brokers(brokers: list[Broker]):
    print("Available brokers:")
    print(" ")
    broker_num = 1
    for broker in brokers:
        print("\t"+str(broker_num)+". "+broker.name)
        broker_num += 1
    print(" ")
    
def main():
    app_config = AppConfig("./config.json")
    if not app_config.check_config():
        print("App config file is missing required parameters")
        exit(-1)
    brokers = init_brokers(app_config.config_data.get('local_config_path'))
    if app_config.config_data.get('mode') == 'interactive':
        print("Interactive mode enabled")
        while(True):
            print(" ")
            print("Options - ")
            print("\t1. List available brokers")
            print("\t2. Authorize and use broker")
            print("\t3. Exit")
            print(" ")
            option_str = input("Enter option: ")
            try:
                option = int(option_str) 
                if option == 1:
                    list_brokers(brokers)
                elif option == 2:
                    broker_name = input("Enter broker name: ")
                    broker_found = False
                    for broker in brokers:
                        if broker.name.lower() == broker_name.lower():
                            broker_found = True
                            print("Authorizing " + broker.name + "...")
                            auth_result = broker.authorize()
                            if auth_result:
                                print("Authorization successful!")
                                broker.run_interactive()
                    if not broker_found:
                        print("Broker not found")
                        continue
                elif option == 3:
                    print("Exiting...")
                    exit(0)
            except ValueError:
                print("Invalid option")
                continue
if __name__ == '__main__':
    main()
   
