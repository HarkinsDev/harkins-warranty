import json
import logging
import requests
from utils.ProcoreAuth import ProcoreAuth

class ProcoreDataFetcher:
    def __init__(self):
        self.procore_auth = ProcoreAuth("procore_tokens.json")
        self.headers = {
            'Authorization': f'Bearer {self.procore_auth.access_token}',
            'Content-Type': 'application/json'
        }
        self.base_url = "https://api.procore.com"
        self.company_id = 3057

    def _format_url(self, endpoint: str) -> str:
        if '?' in endpoint:
            return f"{self.base_url}{endpoint}&company_id={self.company_id}"
        else:
            return f"{self.base_url}{endpoint}?company_id={self.company_id}"

    def get_observation_types(self, project_id: int):
        """Fetch available observation types for a specific project."""
        try:
            endpoint = self._format_url(f"/rest/v1.0/observations/types?project_id={project_id}")
            logging.debug(f"Request URL: {endpoint}")

            response = requests.get(endpoint, headers=self.headers)
            response_data = response.json()

            logging.debug(f"Response Status: {response.status_code}")
            logging.debug(f"Response Data: {json.dumps(response_data, indent=2)}")

            if response.status_code == 200:
                logging.info(f"Successfully fetched observation types for project ID {project_id}.")
                return response_data
            else:
                logging.error(f"Failed to fetch observation types. Status code: {response.status_code}")
                logging.error(f"Response: {json.dumps(response_data, indent=2)}")
                return None
        except Exception as e:
            logging.error(f"Exception occurred while fetching observation types: {e}")
            raise

    def create_observation(self, observation_data, project_id: int):
        """Create a new observation in a specific project."""
        try:
            endpoint = self._format_url("/rest/v1.0/observations/items")
            body = {
                "project_id": project_id,
                "observation": observation_data
            }
            logging.debug(f"Request URL: {endpoint}")
            logging.debug(f"Request Body: {json.dumps(body, indent=2)}")

            response = requests.post(endpoint, headers=self.headers, json=body)
            response_data = response.json()

            logging.debug(f"Response Status: {response.status_code}")
            logging.debug(f"Response Data: {json.dumps(response_data, indent=2)}")

            if response.status_code == 201:
                logging.info(f"Successfully created observation in project ID {project_id}.")
                return response_data
            else:
                logging.error(f"Failed to create observation. Status code: {response.status_code}")
                logging.error(f"Response: {json.dumps(response_data, indent=2)}")
                return None
        except Exception as e:
            logging.error(f"Exception occurred while creating observation: {e}")
            raise
