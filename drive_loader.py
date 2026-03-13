import os, io
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

ROOT_FOLDER_ID = "1QYc7gQx5EkAwR-8WxlNLwED8SNrbvAbA"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDS = os.path.join(os.path.dirname(__file__), 'credentials.json')

def _fix_private_key(pk):
    """
    Normalize private key to proper PEM format regardless of how
    Streamlit Cloud delivers it (literal \\n vs real newlines vs mixed).
    """
    # Step 1: if it contains literal backslash-n, convert to real newlines
    if "\\n" in pk:
        pk = pk.replace("\\n", "\n")

    # Step 2: strip any extra whitespace around the key
    pk = pk.strip()

    # Step 3: ensure the key has proper PEM structure with real newlines
    # Split on the header/footer markers and rebuild cleanly
    pk = pk.replace("-----BEGIN PRIVATE KEY-----", "-----BEGIN PRIVATE KEY-----\n")
    pk = pk.replace("-----END PRIVATE KEY-----", "\n-----END PRIVATE KEY-----")

    # Step 4: collapse any double newlines that may have been created
    while "\n\n" in pk:
        pk = pk.replace("\n\n", "\n")

    # Step 5: ensure it ends with a newline
    if not pk.endswith("\n"):
        pk = pk + "\n"

    return pk

def get_service():
    if os.path.exists(CREDS):
        creds = service_account.Credentials.from_service_account_file(
            CREDS, scopes=SCOPES
        )
    else:
        import streamlit as st
        sa_raw = dict(st.secrets["gcp_service_account"])
        if "private_key" in sa_raw:
            sa_raw["private_key"] = _fix_private_key(sa_raw["private_key"])
        creds = service_account.Credentials.from_service_account_info(
            sa_raw, scopes=SCOPES
        )
    return build('drive', 'v3', credentials=creds, cache_discovery=False)

def list_files(svc, folder_id, mime=None):
    q = f"'{folder_id}' in parents and trashed=false"
    if mime:
        q += f" and mimeType='{mime}'"
    return svc.files().list(q=q, fields='files(id,name)').execute().get('files', [])

def download(svc, file_id):
    buf = io.BytesIO()
    MediaIoBaseDownload(buf, svc.files().get_media(fileId=file_id)).next_chunk()
    buf.seek(0)
    return buf

def find_subfolder(svc, parent, name):
    for f in list_files(svc, parent, 'application/vnd.google-apps.folder'):
        if f['name'] == name:
            return f['id']
    return None

def load_csvs(folder_name):
    svc = get_service()
    fid = find_subfolder(svc, ROOT_FOLDER_ID, folder_name)
    if not fid:
        return []
    return [
        pd.read_csv(download(svc, f['id']))
        for f in list_files(svc, fid)
        if f['name'].endswith('.csv')
    ]

def load_excel(folder_name, filename):
    svc = get_service()
    fid = find_subfolder(svc, ROOT_FOLDER_ID, folder_name)
    if not fid:
        return None
    for f in list_files(svc, fid):
        if f['name'] == filename:
            return pd.ExcelFile(download(svc, f['id']))
    return None
