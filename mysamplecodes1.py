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
from google.oauth2 import service_account

# ---------- GOOGLE SHEETS SETUP ----------
# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"
    ],
)
conn = connect(credentials=credentials)
client=gspread.authorize(credentials)


sheet_id = '1uyxXaNx1qwJBe8pAq_qc_P_xwu0ODBgW6Zba1_IErys/edit?gid=0#gid=0'
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
database_df = pd.read_csv(csv_url, on_bad_lines='skip')

database_df = database_df.astype(str)
sheet_url = st.secrets["https://www.googleapis.com/oauth2/v1/certs"] #this information should be included in streamlit secret
sheet = client.open_by_url(sheet_url).sheet1
sheet.update([database_df.columns.values.tolist()] + database_df.values.tolist())
st.success('Data has been written to Google Sheets')
