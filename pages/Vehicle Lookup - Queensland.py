import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import xlsxwriter 
from selenium.webdriver.chrome.service import Service
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import tempfile
import glob
from streamlit_option_menu import option_menu
from selenium import webdriver


st.set_page_config(
    page_title="Vehicle Registration Lookup",
    layout="wide",
    initial_sidebar_state="expanded",
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def wait_element(browser, s, t=5):
    return WebDriverWait(browser, t).until(EC.presence_of_element_located((By.XPATH,s)))

submit = False
st.image('queensland banner.png')
rego_file = st.file_uploader("Upload List of Registration No. here!",
                                    type="xlsx", 
                                    accept_multiple_files=False)




if rego_file is not None:
    st.markdown("##### Fill file info and mapping")
    with st.form("Mapping form", clear_on_submit=False):
        rego_number = st.text_input(
                "Rego No (Column Name)", placeholder='Rego No'
                )
        sheet_name = st.text_input(
            "Sheet Name" ,placeholder="Sheet1"
            )
        skiprows = st.number_input(
            'Number of rows to skip', min_value=0, step=1
            )
        submit = st.form_submit_button()
        
if submit:
    regos = pd.read_excel(rego_file,sheet_name=sheet_name,skiprows=skiprows)
    rego_list = regos[rego_number].unique().tolist()

    # #For Local
    # options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    # browser = webdriver.Chrome(options=options)
    
    #For server
    service = Service(executable_path=r'/usr/bin/chromedriver')
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(service=service, options=options)

        
    my_progress = st.progress(0)
    status = st.empty()
    dic_all = []
    for i,rego in enumerate(rego_list):
        label = ["Registration Number","Vehicle Identification Number (VIN)", "Description", "Purpose of use", "Status", "Expiry"]
        dic = {}
        browser.get("https://www.service.transport.qld.gov.au/checkrego/public/Welcome.xhtml?dswid=-196")
        wait_element(browser,"//span[text()='Continue']/parent::button").click()
        try:
            wait_element(browser,"//span[text()='Accept']/parent::button").click()
        except:
            pass
        wait_element(browser,"//span[text()='Registration number']/parent::label/following-sibling::input").send_keys(rego)
        wait_element(browser,"//button[@id='vehicleSearchForm:confirmButton']").click()

        try:
            wait_element(browser,"//a[@class='ui-messages-error-summary']")
            for idx,header in enumerate(label):
                dic[header]=""

        except:
            data = browser.find_elements(By.XPATH,f"//dd")
            for idx,header in enumerate(label):
                value = data[idx].text
                dic[header]=value

            dic_all.append(dic)
            pcnt = ((i+1)/len(regos))
            my_progress.progress(pcnt)
            status.write(f"Processing {i+1} of {len(regos)} : {round(pcnt*100,2)}%")
        

    df = pd.DataFrame(dic_all)


    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1',index=False)

    st.download_button(
        label="Download Excel worksheets",
        data=buffer,
        file_name=f"Queensland Rego Lookup Result.xlsx",
        mime="application/vnd.ms-excel"
    )

    browser.quit()