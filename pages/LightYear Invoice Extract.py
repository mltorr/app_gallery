import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import tempfile
import glob
from selenium.common.exceptions import TimeoutException
import os
import shutil
import base64



st.set_page_config(
    page_title="LightYear Automated Invoice Downloader",
    layout="wide",
    initial_sidebar_state="expanded",
)

def wait_element(browser, s, t=20):
    return WebDriverWait(browser, t).until(EC.presence_of_element_located((By.CSS_SELECTOR,s)))

def log():
    st.session_state.log = True
    for k, v in st.session_state.items():
        st.session_state[k] = v

def clear_mfa():
    for i, j in st.session_state.items():
        st.session_state[i] = j
    st.session_state.mfa = False
    
def ent():
    for i, j in st.session_state.items():
        st.session_state[i] = j
    st.session_state.submitted = False

client_name = st.text_input("Client Name:")

file = st.file_uploader("Upload List of URL!",
                type="xlsx", 
                accept_multiple_files=False)



# home = os.path.expanduser("~")
# downloads_directory = os.path.join(home, "Downloads")
temp_dir = tempfile.TemporaryDirectory()

@st.cache_resource(show_spinner=False)
def conn(email,password):
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    service = Service(executable_path=r'/usr/bin/chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('prefs', {
    # Change default directory for downloads
    "download.default_directory": temp_dir.name,
    "download.prompt_for_download": False,  # To auto download the file
    "download.directory_upgrade": True
})
    browser = webdriver.Chrome(service=service, options=options)
    # browser = webdriver.Chrome(options=options)
    browser.get("https://app.lightyear.cloud/login")

    #email-address
    wait_element(browser, "#email-address").send_keys(email)
    #password
    browser.find_element(By.CSS_SELECTOR, "#password").send_keys(password)
    #login-button
    browser.find_element(By.CSS_SELECTOR, "#login-button").click()
    return browser

if 'log' not in st.session_state:
    st.session_state.log = False

if 'mfa' not in st.session_state:
    st.session_state.mfa = False

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

if file is not None:
    urls = pd.read_excel(file,header=None)
    url_list = urls[0].unique().tolist()
    if not st.session_state.log:
        with st.form("login"):
            st.markdown("#### Enter your credentials")
            st.text_input("Email",key='email')
            st.text_input("Password", type="password",key='password')
            logged = st.form_submit_button("Login",on_click=log)
            # placeholder.empty()

    if st.session_state.log:
        
        with st.spinner('In progress...'):
            browser = conn(st.session_state.email,st.session_state.password)
            # try:
            #     conn(browser,st.session_state.email,st.session_state.password)
            # except AttributeError as e:
            #     pass
        if wait_element(browser, "#code") is not None:
            st.session_state.mfa = True
        if st.session_state.mfa:
            code = st.text_input("Code",key='code')
            #code
            browser.find_element(By.CSS_SELECTOR, "#code").send_keys(st.session_state.code)
            #click Verify
            browser.find_element(By.CSS_SELECTOR, "#mat-dialog-0 > lightyear-sms-code-dialog > div > div.mat-dialog-actions.action-buttons-container > button.primary-button").click()

            time.sleep(5)


            #Select Entity
            try:
                with st.spinner('In progress...'):
                    wait_element(browser, "#mat-dialog-1 > lightyear-company-picker-dialog > div > div.mat-dialog-content.dialog-content > lightyear-company-picker > mat-table > mat-row > mat-cell.mat-cell.cdk-cell.cdk-column-companyName.mat-column-companyName.ng-star-inserted").click()

                    for url in url_list: 
                        browser.get(url)
                        wait_element(browser,"#container > div:nth-child(5) > button:nth-child(2) > mat-icon").click()
                        # filepath = f"{temp_dir}/{client_name}"
                        # shutil.make_archive(filepath, 'zip', temp_dir.name)

                        # with open(filepath, "rb") as file:
                        #     btn = st.download_button(
                        #     label = "Download Invoices",
                        #     data = file,
                        #     file_name = f"{client_name}.zip",
                        #     mime = "application/zip"
                        # )
                    
                        # st.write(f"[Download Zip File]({filepath})")

                        # with open(temp_dir.name, "rb") as f:
                        #     bytes = f.read()
                        #     b64 = base64.b64encode(bytes).decode()
                        #     href = f'<a href="data:file/zip;base64,{b64}" download=\'{client_name}.zip\'>\
                        #         Click to download\
                        #     </a>'
                        # st.markdown(href, unsafe_allow_html=True)
                        st.write("Kuking ng Ina mo!!!!")

                        if st.button("Zip and Download PDFs"):
                            zip_filename = os.path.join(temp_dir.name, f"{client_name}.zip")

                            pdf_temp_dir = tempfile.mkdtemp()

                            for pdf_file in glob.glob(f"{temp_dir.name}/*.pdf"):
                                shutil.move(pdf_file, os.path.join(pdf_temp_dir, os.path.basename(pdf_file)))

                            shutil.make_archive(zip_filename[:-4], 'zip', pdf_temp_dir)

                            # shutil.rmtree(pdf_temp_dir)

                            st.success("PDF files zipped successfully!")

                            st.markdown(f"[Download Zip File]({zip_filename})")   
            except TimeoutException as e:
                    pass



reset = st.button("Reset")
if reset:
    st.cache_resource.clear()