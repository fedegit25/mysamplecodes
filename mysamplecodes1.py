import streamlit as st
import pandas as pd
from datetime import datetime
import io
import gspread
from google.oauth2.service_account import Credentials
import barcode
from barcode.writer import ImageWriter
from PIL import Image

# ---------- GOOGLE SHEETS SETUP ----------
# Load credentials from Streamlit Cloud secrets
creds_dict = dict(st.secrets)

# Open Google Sheet
SPREADSHEET_NAME = 'Mysamplecodes'
SHEET_NAME = 'Sheet1'

def connect_to_gsheet(creds_dict, spreadsheet_name, sheet_name):
    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    spreadsheet = client.open(spreadsheet_name)
    return spreadsheet.worksheet(sheet_name)

sheet_by_name = connect_to_gsheet(creds_dict, SPREADSHEET_NAME, SHEET_NAME)

# ---------- Streamlit App ----------
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
    with st.form(key="data_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120)
        email = st.text_input("Email")
        submitted = st.form_submit_button("Submit")
        if submitted:
            if name and email:
                add_data([name, age, email])
                st.success("Data added successfully!")
            else:
                st.error("Please fill out the form correctly.")

# Display data
st.header("Data Table")
df = read_data()
st.dataframe(df, width=800, height=400)
