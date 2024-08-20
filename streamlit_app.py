import streamlit as st
from utils.ProcoreDataManager import ProcoreDataFetcher
from utils.SnowflakeConnector import SnowflakeConnection  # Ensure this path is correct

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

    # Retrieve query parameters
    query_params = st.query_params()
    form_response_id = query_params.get('form_response_id', [None])[0]

    fetcher = ProcoreDataFetcher()

    # Debugging statement to ensure the module is imported correctly
    try:
        snowflake_conn = SnowflakeConnection()
    except NameError as e:
        st.error(f"Failed to initialize SnowflakeConnection: {str(e)}")
        return

    # Fetch tracking numbers from Snowflake
    tracking_numbers = snowflake_conn.get_tracking_numbers()
    
    # If form_response_id is provided, use it to pre-select the tracking number
    selected_tracking = None
    if form_response_id:
        selected_tracking = snowflake_conn.get_tracking_number_by_form_response_id(form_response_id)
        if selected_tracking not in tracking_numbers:
            st.error("Invalid form response ID or tracking number not found.")
            return
    else:
        selected_tracking = st.selectbox("Select Tracking Number", tracking_numbers)

    if selected_tracking:
        # Fetch the warranty response based on the selected tracking number
        warranty_response = snowflake_conn.get_warranty_response_by_tracking(selected_tracking)

        # Populate the form fields with fetched data
        if warranty_response:
            st.write("**Responder:**", warranty_response.get("RESPONDER"))
            st.write("**Submit Date:**", warranty_response.get("SUBMITDATE"))
            st.write("**Address:**", warranty_response.get("ADDRESS"))
            st.write("**Appliance Issue:**", warranty_response.get("ISAPPLIANCEISSUE"))
            st.write("**Primary Contact:**", warranty_response.get("PRIMARYCONTACT"))
            st.write("**Priority:**", warranty_response.get("PRIORITY"))
            st.write("**Issue Description:**", warranty_response.get("ISSUEDESCRIPTION"))
            st.write("**Location:**", warranty_response.get("LOCATION"))

    description = st.text_area("Description of the Issue", value=warranty_response.get("ISSUEDESCRIPTION", ""))
    name = st.text_input("Observation Name", value="Warranty Observation")
    submit_button = st.button("Submit")

    if submit_button:
        if selected_tracking and description and name:
            observation_data = {
                "description": description,
                "name": name,
                "type_id": 32591,  # Presumed warranty type ID
                "observation_type": {
                    "id": 32591  # Assumes this is the type ID for warranty
                }
            }
            new_observation = fetcher.create_observation(observation_data, int(selected_tracking))
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
