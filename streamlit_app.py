import streamlit as st
from utils.ProcoreDataManager import ProcoreDataFetcher

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login screen
def login_screen():
    st.title("🔒 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        # Replace with your authentication logic
        if username == "admin" and password == "password":
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password")

# Warranty Observation submission page
def warranty_observation_page():
    st.title("🛠️ Submit Warranty Observation")

    fetcher = ProcoreDataFetcher()

    # Inputs for the Warranty Observation
    project_id = st.text_input("Project ID", value="490956")  # Example default project ID
    description = st.text_area("Description of the Issue")
    name = st.text_input("Observation Name", value="Warranty Observation")
    submit_button = st.button("Submit")

    if submit_button:
        if project_id and description and name:
            observation_data = {
                "description": description,
                "name": name,
                "type_id": 32591,  # Presumed warranty type ID
                "observation_type": {
                    "id": 32591  # Assumes this is the type ID for warranty
                }
            }
            new_observation = fetcher.create_observation(observation_data, int(project_id))
            if new_observation:
                st.success("Warranty observation submitted successfully!")
                st.write("New Observation:", new_observation)
            else:
                st.error("Failed to submit the observation. Please try again.")
        else:
            st.error("Please fill in all fields before submitting.")

# Main app logic
if st.session_state.logged_in:
    warranty_observation_page()
else:
    login_screen()
