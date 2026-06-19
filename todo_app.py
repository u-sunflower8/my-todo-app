import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.write("接続テスト開始")

try:
    # Secretsから取得
    creds_dict = st.secrets["GOOGLE_SHEETS"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_dict, 
        ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    )
    client = gspread.authorize(creds)
    sheet = client.open("Todoリスト").sheet1
    st.write("シート接続成功！")
    st.write(sheet.get_all_records())
except Exception as e:
    st.error(f"エラー発生: {e}")
