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

# Create authorized gspread client
creds = Credentials.from_service_account_info(creds_dict)
gc = gspread.authorize(creds)

# Open Google Sheet
sheet = gc.open("Mysamplecodes").sheet1
records = sheet.get_all_records()

# ---------- UI ----------
st.title("📦 Sample Barcode Logger & Search")

tab1, tab2 = st.tabs(["➕ Generate Barcode", "🔍 Search Samples"])

with tab1:
    st.header("➕ Generate New Sample")

    # Input fields
    project = st.text_input("Project Name")
    injection_number = st.number_input("Injection Number", min_value=1, step=1)
    sample_mode = st.selectbox("Sample Mode", ["Manual", "Auto", "Other"])
    volume = st.number_input("Sample Volume (μL)", min_value=0, step=1)
    generate = st.button("Generate Barcode and Save")

    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if generate:
        today = datetime.now().strftime("%Y%m%d")
        sample_name = f"{today}_{project}_{injection_number}_{sample_mode}_{volume}uL"

        # Generate barcode
        barcode_class = barcode.get_barcode_class('code128')
        barcode_obj = barcode_class(sample_name, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_obj.write(buffer)
        buffer.seek(0)

        # Display & download barcode
        st.image(buffer, caption="Sample Barcode")
        st.download_button(
            label="⬇️ Download Barcode PNG",
            data=buffer,
            file_name=f"{sample_name}.png",
            mime="image/png"
        )

        # Log to Google Sheet
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, sample_name, project, injection_number, sample_mode, volume]
        sheet.append_row(row)
        st.session_state['history'].append(row)
        st.success("Sample logged successfully.")

    # Display recent entries
    if st.session_state['history']:
        st.subheader("Recent Session Entries")
        df = pd.DataFrame(st.session_state['history'],
                          columns=["Timestamp", "Sample Name", "Project", "Injection", "Mode", "Volume (μL)"])
        st.dataframe(df)

        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_buffer.getvalue(),
            file_name="sample_records.csv",
            mime="text/csv"
        )

with tab2:
    st.header("🔍 Search by Barcode")
    search_input = st.text_input("Scan or Type Barcode Sample Name")

    if search_input:
        df_records = pd.DataFrame(records)
        result = df_records[df_records["Sample Name"] == search_input]

        if not result.empty:
            st.success("Match found:")
            st.dataframe(result)
        else:
            st.error("No matching sample found.")
