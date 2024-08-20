import os
import gzip
import json
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobLeaseClient
from dotenv import load_dotenv

load_dotenv()

class AzureBlobUtils:

    def __init__(self):
        # Load the connection string from environment variables
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not self.connection_string:
            raise ValueError("Azure Storage connection string not found in environment variables.")

        self.container_name = "procore-raw"
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    def upload_to_blob(self, data, blob_name):
        blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
        if isinstance(data, (dict, list, bytes)):
            data = json.dumps(data)
        blob_client.upload_blob(data, overwrite=True)
        print("TRUE")

    def upload_todo_list(self, endpoint, data):
        todo_list_name = f"{endpoint}/{endpoint}_todo.json"
        print(todo_list_name)
        self.upload_to_blob(data, todo_list_name)
    
    def get_file_content(self, blob_name):
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_data = blob_client.download_blob()
        byte_content = blob_data.readall()
        
        # Decode byte string to normal string
        str_content = byte_content.decode("utf-8")
        
        # Parse JSON string to Python data structure
        return json.loads(str_content)

    def get_todo_list(self, endpoint):
        todo_list_file_name = f"{endpoint}/{endpoint}_todo.json"
        try:
            return self.get_file_content(todo_list_file_name)
        except Exception as e:
            print(f"Oi, sumthin' went pear-shaped: {e}")
            return None

    def count_blobs_in_folder(self, folder_name):
        blob_list = self.container_client.list_blobs(name_starts_with=folder_name)
        return len([blob.name for blob in blob_list])
        
    def get_data_from_blob(self, blob_name):
            blob_client = self.blob_service_client.get_blob_client(container=self.container_name, blob=blob_name)
            blob_data = blob_client.download_blob().readall()
            json_data = json.loads(blob_data)
            return json_data
        
    def update_tokens_in_blob(self, blob_name, new_access_token, new_refresh_token):
        existing_data = self.get_data_from_blob(blob_name)
        existing_data['access_token'] = new_access_token
        existing_data['refresh_token'] = new_refresh_token
        self.upload_to_blob(existing_data, blob_name)

    def upload_batch_to_blob(self, batch_data, endpoint):
        
        if batch_data is None or endpoint is None:
            return 'Batch upload failed. Check yer logs.'

        batch_number = self.count_blobs_in_folder(endpoint)
        
        folder_name = f"{endpoint}/"
        blob_name = f"{folder_name}{endpoint}_batch_{batch_number}.json"
        
        self.upload_to_blob(batch_data, blob_name)
        return "Batch uploaded successfully."

    def delete_all_blobs_in_folder(self, folder_name):
        blob_list = self.container_client.list_blobs(name_starts_with=folder_name)
        for blob in blob_list:
            self.container_client.delete_blob(blob.name)


    def break_lease_on_all_blobs(self, container_name):
        container_client = self.blob_service_client.get_container_client(container=container_name)
        blob_list = container_client.list_blobs()
        
        for blob in blob_list:
            blob_client = container_client.get_blob_client(blob=blob.name)
            lease_client = BlobLeaseClient(blob_client)
            try:
                # Attempt to break the lease
                lease_client.break_lease()
                print(f"Broke lease on: {blob.name}, bare skills!")
            except Exception as e:
                print(f"Couldn't break lease on {blob.name}, 'cause of this ting: {e}")
                
    def delete_all_blobs_except_procore_tokens(self, container_name):
        container_client = self.blob_service_client.get_container_client(container=container_name)
        blob_list = container_client.list_blobs()

        for blob in blob_list:
            if blob.name != 'procore_tokens.json':
                try:
                    container_client.delete_blob(blob.name)
                    print(f"Deleted blob: {blob.name}, it's gone, kaput!")
                except Exception as e:
                    print(f"Oi, can't delete {blob.name}, 'cause of this malarkey: {e}")
