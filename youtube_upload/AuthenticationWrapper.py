import httplib, urllib, json
import abc
import gdata.youtube.service

REQUEST_HEADERS = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
GOOGLE_ACCOUNTS_DOMAIN = "accounts.google.com"
GOOGLE_OAUTH2_TOKEN_PATH = "/o/oauth2/token"
GRANT_TYPE_PARAM_VALUE = "refresh_token"
ACCESS_TOKEN_KEY = "access_token"

def _get_url_encoded_request_params(refresh_token, oauth_client_id, oauth_client_secret):
    """
    Build form parameters.
    """
    params = {
              "client_id": oauth_client_id,
              "client_secret": oauth_client_secret,
              "refresh_token": refresh_token,
              "grant_type": GRANT_TYPE_PARAM_VALUE
              }
    return urllib.urlencode(params)

def _get_access_token_from_json_message(json_message):
    """
    Extract the access token value from a json message.
    """
    decodedJson = json.loads(json_message)
    return decodedJson[ACCESS_TOKEN_KEY]

def exchange_oauth_refresh_token_for_access_token(refresh_token, oauth_client_id, oauth_client_secret):
    """
    HTTP POST to Google to exchange an OAuth2 refresh token for an access token.
    """
    params = _get_url_encoded_request_params(refresh_token, oauth_client_id, oauth_client_secret)
    connection = httplib.HTTPSConnection(GOOGLE_ACCOUNTS_DOMAIN)
    connection.request("POST", GOOGLE_OAUTH2_TOKEN_PATH, params, REQUEST_HEADERS)
    response = connection.getresponse()
    jsonMessage = response.read()
    connection.close()
    accessToken = _get_access_token_from_json_message(jsonMessage)
    return accessToken

class BaseAuthenticatedWrapper(object):
    """
    Abstract class for authenticated interaction with the YouTube API.
    """
    __metaclass__ = abc.ABCMeta
    
    DEFAULT_UPLOADER = "default"
    
    def __init__(self, developer_key, app_name):
        self._developer_key = developer_key
        self._app_name = app_name
        self.youtube_service = gdata.youtube.service.YouTubeService(source = self._app_name, developer_key = self._developer_key)    
    
    @abc.abstractmethod
    def authenticate(self):
        """
        Abstract method to authenticate with the YouTube API.
        """
        return   
    
    def is_authentication_valid(self):
        """"
        It is only possible to retrieve the default user profile if the API has been authenticated.
        The username "default" represents the authenticated user.
        """
        try:            
            self.youtube_service.GetYouTubeUserEntry(username= self.DEFAULT_UPLOADER)
            return True
        except:
            return False

class InvalidRefreshToken(Exception): pass
            
class TokenAuthenticatedWrapper(BaseAuthenticatedWrapper):
    """
    Allows for authentication to the YouTube API using a refresh token.
    """
    def __init__(self, developer_key, app_name, refresh_token, oauth_client_id, oauth_client_secret):    
        super(TokenAuthenticatedWrapper, self).__init__(developer_key, app_name)
        
        self._refresh_token = refresh_token
        self._oauth_client_id = oauth_client_id
        self._oauth_client_secret = oauth_client_secret
                    
    def _is_refresh_token_valid(self):
        try:
            self._exchange_refresh_token_for_access_token()
            return True
        except:
            return False
                      
    def _exchange_refresh_token_for_access_token(self):
        self._exchanged_token = exchange_oauth_refresh_token_for_access_token(self._refresh_token, self._oauth_client_id, self._oauth_client_secret)
        
    def authenticate(self):
        """
        Will raise InvalidRefreshToken if the refresh token is invalid.
        """
        if self._is_refresh_token_valid():       
            self.youtube_service.SetAuthSubToken(self._exchanged_token)
        else:
            raise InvalidRefreshToken("The refresh token is invalid.")
    
class CredentialAuthenticatedWrapper(BaseAuthenticatedWrapper):
    """
    ALlows for authentication to the YouTube API using ClientLogin (plain text username and password).
    """
    def __init__(self, developer_key, app_name, email, password):
        super(CredentialAuthenticatedWrapper, self).__init__(developer_key, app_name)
        
        self._email = email
        self._password = password
        
    def authenticate(self):
        self.youtube_service.email = self._email
        self.youtube_service.password = self._password
        self.youtube_service.ProgrammaticLogin()
