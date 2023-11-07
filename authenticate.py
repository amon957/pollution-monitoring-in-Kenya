def authenticate(ee):
    service_account='streamlit-projects@ee-amon-melly.iam.gserviceaccount.com'
    key='key/ee-amon-melly-b01b9adf906a.json'
    
    credentials = ee.ServiceAccountCredentials(service_account, key)
    ee.Initialize(credentials)
    return(ee)