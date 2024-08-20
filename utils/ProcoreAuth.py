import http.client
import json
import logging
from typing import Dict, Optional
from utils.AzureBlobMGMT import AzureBlobUtils

class ProcoreAuth:

    COMMON_HEADERS = {'Content-Type': 'application/json'}

    def __init__(self, filename):
        self.filename = filename
        self.conn = http.client.HTTPSConnection("api.procore.com")
        self.azure_blob_utils = AzureBlobUtils()
        self.load_credentials_and_tokens()


    def load_credentials_and_tokens(self):
        data: Dict = self.azure_blob_utils.get_data_from_blob(self.filename)
        self.client_id: Optional[str] = data.get('client_id')
        self.client_secret: Optional[str] = data.get('client_secret')
        self.redirect_uri: Optional[str] = data.get('redirect_uri')
        self.access_token: Optional[str] = data.get('access_token')
        self.refresh_token: Optional[str] = data.get('refresh_token')
        self.headers: Dict[str, str] = self.COMMON_HEADERS.copy()
        self.update_authorization_header()


    def update_authorization_header(self):
        if self.access_token:
            self.headers['Authorization'] = f"Bearer {self.access_token}"
            
    def save_tokens_to_blob(self):
            try:
                data = {
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'redirect_uri': self.redirect_uri,
                    'access_token': self.access_token,
                    'refresh_token': self.refresh_token
                }
                self.azure_blob_utils.upload_to_blob(data, self.filename)
            except Exception as e:
                logging.error(f"Failed to save tokens: {e}")    

    def refresh_tokens(self):
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token
        }
        self.conn.request("POST", "/oauth/token", body=json.dumps(payload), headers=self.COMMON_HEADERS)
        response = self.conn.getresponse()
        data = json.loads(response.read().decode("utf-8"))

        if response.status == 200:
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            self.update_authorization_header()
            self.save_tokens_to_blob()
        else:
            logging.error(f"Failed to refresh tokens: {data.get('error_description', 'Unknown error')}")


