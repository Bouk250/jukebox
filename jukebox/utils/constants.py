from requests.sessions import DEFAULT_REDIRECT_LIMIT


TIDAL_URL_PRE = 'https://api.tidalhifi.com/v1/'
TIDAL_AUTH_URL = 'https://auth.tidal.com/v1/oauth2/'
# known API key for Fire Stick HD(MQA, Dolby Vision enabled)
TIDAL_API_KEY = {'clientId': 'aR7gUaTK1ihpXOEP', 'clientSecret': 'eVWBEkuL2FCjxgjOkR3yK0RYZEbcrMXRc2l8fU3ZCdE='}

API_CALL_TIMEOUT = 30

DEEZER_GWAPI_URL = "http://www.deezer.com/ajax/gw-light.php"
DEEZER_API_URL = "https://api.deezer.com/"