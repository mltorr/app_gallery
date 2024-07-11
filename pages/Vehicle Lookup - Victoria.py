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
import undetected_chromedriver as uc 
from selenium.webdriver.chrome.options import Options
from selenium_profiles.webdriver import Chrome
from selenium_profiles.profiles import profiles
from seleniumwire import webdriver
import utils

utils.setup_page("VHR - Victoria")


# st.set_page_config(
#     page_title="Vehicle Registration Lookup",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def wait_element(browser, s, t=5):
    return WebDriverWait(browser, t).until(EC.presence_of_element_located((By.XPATH,s)))



submit = False
st.image('vic banner.png')
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
    # profile = profiles.Windows() # or .Android
    # options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")
    # browser = Chrome(profile, options=options,
    #                 uc_driver=False
    #                 )
    
    #For server
    service = Service(executable_path=r'/usr/bin/chromedriver')
    profile = profiles.Windows() # or .Android
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    browser = Chrome(profile, 
                    options=options,
                    uc_driver=False,
                    service=service
                    )

        
    my_progress = st.progress(0)
    status = st.empty()

    dic_all = []
    for i,rego in enumerate(rego_list):
        dic = {rego_number:rego}
        label = ["Registration status & expiry date"
                    ,"Vehicle"
                    ,"VIN/Chassis"
                    ,"Engine number"
                    ,"Registration serial number"
                    ,"Compliance plate / RAV entry date"
                    ,"Sanction(s) applicable"
                    ,"Goods carrying vehicle"
                    ,"Transfer in dispute"]
        try:
            browser.get("https://www.vicroads.vic.gov.au/registration/buy-sell-or-transfer-a-vehicle/check-vehicle-registration/vehicle-registration-enquiry")
            time.sleep(2)
            #Input Rego Number
            wait_element(browser,"//label[text()='Registration number ']/following-sibling::input").clear()
            wait_element(browser,"//label[text()='Registration number ']/following-sibling::input").send_keys(rego)
            element = wait_element(browser,"//input[@id='ph_pagebody_0_phthreecolumnmaincontent_1_panel_btnSearch']")
            browser.execute_script("arguments[0].click();", element)

            for j in label:
                k = wait_element(browser,f"//label[text()='{j}:']/following-sibling::div").text
                dic[j] = k

        except:
            for j in label:
                dic[j] = ""

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
        file_name=f"VIC Rego Lookup Result.xlsx",
        mime="application/vnd.ms-excel"
    )

    browser.quit()
