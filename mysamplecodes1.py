import streamlit as st
import pandas as pd
from datetime import datetime
import io
import gspread
import json
from google.oauth2.service_account import Credentials
import barcode
from barcode.writer import ImageWriter
from PIL import Image

# ---------- GOOGLE SHEETS SETUP ----------
# Load credentials from Streamlit Cloud secrets
creds_dict = dict(st.secrets)  # works in Streamlit Cloud (flat keys only)
def connect_to_gsheet(creds_dict, spreadsheet_name, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds",
             'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
             


# Create authorized gspread client

creds = Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets"])
client = gspread.authorize(creds)
spreadsheet = client.open(SPREADHSEET_NAME)  

# Open Google Sheet
SPREADSHEET_NAME = 'Mysamplecodes'
SHEET_NAME = 'Sheet1'

sheet_by_name = connect_to_gsheet(creds, SPREADSHEET_NAME, sheet_name=SHEET_NAME) 

st.title("Simple Data Entry using Streamlit")

# Read Data from Google Sheets
def read_data():
    data = sheet_by_name.get_all_records()  # Get all records from Google Sheet
    return pd.DataFrame(data)

# Add Data to Google Sheets
def add_data(row):
    sheet_by_name.append_row(row)  # Append the row to the Google Sheet

# Sidebar form for data entry
with st.sidebar:
    st.header("Enter New Data")
    # Assuming the sheet has columns: 'Name', 'Age', 'Email'
    with st.form(key="data_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        email = st.text_input("Email")
        # Submit button inside the form
        submitted = st.form_submit_button("Submit")
        # Handle form submission
        if submitted:
            if name and email:  # Basic validation to check if required fields are filled
                add_data([name, age, email])  # Append the row to the sheet
                st.success("Data added successfully!")
            else:
                st.error("Please fill out the form correctly.")

# Display data in the main view
st.header("Data Table")
df = read_data()
st.dataframe(df, width=800, height=400)
