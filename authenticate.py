import json2
import streamlit as st
def authenticate(ee):
    key = 'county_shapefile/ee-amon-melly-b01b9adf906a.json'
    service_account=st.secrets.account
    credentials = ee.ServiceAccountCredentials(service_account, key)
    ee.Initialize(credentials)
    return(ee)
