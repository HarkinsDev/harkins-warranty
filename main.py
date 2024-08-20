from utils.ProcoreDataManager import ProcoreDataFetcher
import logging

import logging

import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    fetcher = ProcoreDataFetcher()

    project_id = 490956
    observation_data = {
                "description": "Test Observation Item",
                "name": "Test Observation",
                "type_id": 32591,  # Use type_id
                "observation_type": {
                    "id": 32591  # Nest under observation_type as well
                }
            }

    new_observation = fetcher.create_observation(observation_data, project_id)
    print("New Observation:", new_observation)
