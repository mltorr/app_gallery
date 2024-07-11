import streamlit as st
import msal
import requests
from urllib.parse import urlencode, urlparse, parse_qs

CLIENT_ID = 'c67433d1-4b9f-4390-98eb-9a67393e5c51'
CLIENT_SECRET = 'Cg68Q~EdFws0rii6ZMD5eMQtqyhcVSk76ON9tbuj'
TENANT_ID = 'e4f18beb-5183-4e96-9089-00c5739245db'

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["User.ReadBasic.All"]
REDIRECT_URI = 'http://localhost:8501/'

app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)

def get_auth_url():
    auth_url = app.get_authorization_request_url(SCOPE, redirect_uri=REDIRECT_URI)
    return auth_url

def get_token_from_code(auth_code):
    result = app.acquire_token_by_authorization_code(auth_code, scopes=SCOPE, redirect_uri=REDIRECT_URI)
    return result.get('access_token')

def get_user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    return response.json()

def handle_redirect():
    if not st.session_state.get('access_token'):
        query_params = st.query_params
        if 'code' in query_params:
            code = query_params['code']
            access_token = get_token_from_code(code)
            if access_token:
                st.session_state['access_token'] = access_token
                # Clear query parameters by redirecting to the same page without the 'code' parameter
                # st.experimental_set_query_params(code=None)

def logout():
    if 'access_token' in st.session_state:
        del st.session_state['access_token']
