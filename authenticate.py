import json2
import streamlit as st
def authenticate(ee):
    secret_key = st.secrets.json_key
    key = json2.loads(secret_key)
    service_account=st.secrets.account
    credentials = ee.ServiceAccountCredentials(service_account, key)
    ee.Initialize(credentials)
    return(ee)
