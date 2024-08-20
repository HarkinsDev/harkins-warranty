from utils.ProcoreDataManager import ProcoreDataFetcher
import logging

import logging

import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    fetcher = ProcoreDataFetcher()

    project_id = 490956

    # Fetch observation types to use a valid type ID
    observation_types = fetcher.get_observation_types(project_id)
    if observation_types is None:
        logging.error("Failed to fetch observation types. Aborting operation.")
    else:
        # Use the first available observation type for testing
        if observation_types:
            type_id = observation_types[0]["id"]  # Adjust as needed to pick a valid type
        else:
            logging.error("No observation types available. Aborting operation.")
            type_id = None

        if type_id:
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
