import os
import json
import snowflake.connector
from dotenv import load_dotenv
import streamlit as st

class SnowflakeConnection:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.config = self.get_snowflake_config()
        self.connection = self.get_snowflake_connection()
        
    def get_snowflake_config(self) -> dict:
        try:
            config = {
                "account": os.getenv("SNOWFLAKE_ACCOUNT"),
                "user": os.getenv("SNOWFLAKE_USER"),
                "password": os.getenv("SNOWFLAKE_PASSWORD"),
                "database": os.getenv("SNOWFLAKE_DATABASE"),
                "schema": os.getenv("SNOWFLAKE_SCHEMA"),
                "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
                "role": os.getenv("SNOWFLAKE_ROLE", "SYSADMIN"),  # Default to SYSADMIN if role is not provided
            }

            if None in config.values():
                missing_keys = [k for k, v in config.items() if v is None]
                raise KeyError(f"Missing environment variables: {', '.join(missing_keys)}")

        except KeyError as e:
            raise KeyError(f"Environment variable {str(e)} is missing or empty") from e

        return config

    def get_snowflake_connection(self):
        try:
            conn = snowflake.connector.connect(
                account=self.config['account'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                schema=self.config['schema'],
                warehouse=self.config['warehouse'],
                role=self.config['role']
            )
            return conn
        except snowflake.connector.errors.Error as e:
            print(f"Error connecting to Snowflake: {str(e)}")
            raise

    def execute_query(self, query: str) -> list:
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except snowflake.connector.errors.ProgrammingError as e:
            print(f"Error executing query: {str(e)}")
            raise

    def get_tracking_numbers(self) -> list:
        query = "SELECT TRACKINGNUMBER FROM STANDARD_DB.WARRANTY.WARRANTY_FORM_RESPONSE"
        return [row[0] for row in self.execute_query(query)]

    def get_warranty_response_by_tracking(self, tracking_number: str) -> dict:
        query = f"SELECT * FROM WARRANTY_FORM_RESPONSE WHERE TRACKINGNUMBER = '{tracking_number}'"
        result = self.execute_query(query)
        if result:
            columns = ["RESPONDER", "SUBMITDATE", "ADDRESS", "ISAPPLIANCEISSUE", "PRIMARYCONTACT",
                       "PRIORITY", "TRACKINGNUMBER", "DATE", "UNITOCCUPIED", "JOBNUMBER",
                       "ISSUEDESCRIPTION", "PROPERTYINFORMATION", "PROPERTYNAME",
                       "NOTETOTRADEPARTNERS", "LOCATION", "APPLIANCEMODELSERIAL"]
            return dict(zip(columns, result[0]))
        return {}