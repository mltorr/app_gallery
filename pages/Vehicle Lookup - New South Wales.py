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
st.image('nsw banner.png')
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
        try:
            browser.get("https://free-rego-check.service.nsw.gov.au/")
            #Enter Plate Number
            wait_element(browser,"//input[@id='plateNumberInput']").clear()
            wait_element(browser,"//input[@id='plateNumberInput']").send_keys(rego)
            
            #Accept Terms and Conditions
            browser.find_element(By.XPATH, "//input[@id='termsAndConditions']").click()
            
            #Check Registration
            browser.find_element(By.XPATH, "//button[text()='Check registration']").click()
            
            #Make
            make = wait_element(browser,"//div[text()='Make']/following-sibling::div").text
            
            #Model
            model = browser.find_element(By.XPATH, "//div[text()='Model']/following-sibling::div").text
            
            #Variant
            try:
                variant = browser.find_element(By.XPATH, "//div[text()='Variant']/following-sibling::div").text
            except:
                variant = ''
            
            #Colour
            try:
                colour = browser.find_element(By.XPATH, "//div[text()='Colour']/following-sibling::div").text
            except:
                colour = ''
            
            #Shape
            try:
                shape = browser.find_element(By.XPATH, "//div[text()='Shape']/following-sibling::div").text
            except:
                shape = ''
            
            #Manufacture Year
            try:
                manufacture_year = browser.find_element(By.XPATH, "//div[text()='Manufacture year']/following-sibling::div").text
            except:
                manufacture_year = ''
            
            
            #Gross Vehicle Mass
            try:
                gross_vehicle_mass = browser.find_element(By.XPATH, "//div[text()='Gross vehicle mass']/following-sibling::div").text
            except:
                gross_vehicle_mass = ''
                
            #Nominated Configuration
            try:
                nomitated_configuration = browser.find_element(By.XPATH, "//div[text()='Nominated configuration']/following-sibling::div").text
            except:
                nomitated_configuration = ''
                
            #Registration concession
            try:
                registration_concession = browser.find_element(By.XPATH, "//div[text()='Registration concession']/following-sibling::div").text
            except:
                registration_concession = ''
                
            #Condition codes
            try:
                condition_codes = browser.find_element(By.XPATH, "//div[text()='Condition codes']/following-sibling::div").text
            except:
                condition_codes = ''
                
            #Odometer readings 
            try:
                browser.find_element(By.XPATH, "//button[text()='Show more']").click()
                time.sleep(2)
                odometer = browser.find_element(By.XPATH, "//div[text()='Odometer readings*']/following-sibling::div").text
            except:
                odometer = ''
                
            dic = {
                rego_number:rego
                ,"Make":make
                ,"Mode":model
                ,"Variant":variant
                ,"Colour":colour
                ,"Shape":shape
                ,"Manufacture Year":manufacture_year
                ,"Gross Vehicle Mass":gross_vehicle_mass
                ,"Nominated Configuration":nomitated_configuration
                ,"Registration concession":registration_concession
                ,"Condition codes":condition_codes
                ,"Odometer Readings":odometer
                }
        except:
            dic = {
                    rego_number:rego
                    ,"Make":""
                    ,"Mode":""
                    ,"Variant":""
                    ,"Colour":""
                    ,"Shape":""
                    ,"Manufacture Year":""
                    ,"Gross Vehicle Mass":""
                    ,"Nominated Configuration":""
                    ,"Registration concession":""
                    ,"Condition codes":""
                    ,"Odometer Readings":""
                    }

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
        file_name=f"NSW Rego Lookup Result.xlsx",
        mime="application/vnd.ms-excel"
    )

    browser.quit()