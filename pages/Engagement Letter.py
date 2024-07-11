
from docxtpl import DocxTemplate
import pandas as pd
import streamlit as st
import requests
import json
import re
import zipfile
import os


st.set_page_config(
    page_title="Engagement Letter",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

def delete_paragraph(paragraph):
    p = paragraph._element
    p.getparent().remove(p)
    p._p = p._element = None

def Delete_table(document,table):
        document.tables[table]._element.getparent().remove(document.tables[table]._element)

def abn_check(abn,url,gui):
    u = f'{url}abn={abn}&guid={gui}'
    r = requests.get(u)
    data = r.text
    cleanse_data = re.sub(r'\(|\)|\bcallback\b',"",data)
    return json.loads(cleanse_data)

### Set Default Value to parameters
### Parameters for to_delete
ita_ind = lta_ind = il_ind = aas_ind = test_ind = rfi_ind = draft_ind = lta_sec_ind ="to_delete"
il_word = "indirect"


#### Initialize empty list
selected_ts = [] ### Indirect Tax Analysis - Tax Scopes
selected_ita_lta =[] ### Title for Indirect Tax Only, Land Tax Only or Both

## Column name for Table Fee and Selected Scopes from Assurance and Advisory Services 
selected_aas = []
colname = ["Scoping Item","Fees"]


### Selected Test Category and Tax Scopes
### If category has GST
selected_test_cat = ap_ar = with_gst = ""

st.title("Engagement Letter")
st.markdown("This will generate an engagement letter base on selected parameters")

######## Forms ########
c1,c2 = st.columns(2)

with c1:

    st.markdown("##### ABN Checker:")
    with st.container(border=True):
        y1,y2 = st.columns([8,2])
        with y1:
            abn = st.text_input('ABN')
            abn_res = abn_check(abn,st.secrets.url,st.secrets.gui)
        with y2:
            st.write('')
            st.write('')
            btn_check = st.button("Check")
        if btn_check:
            if abn_res['AbnStatus']=='Active':
                st.success('This is a valid ABN and Active')
                st.write(f"Entity Name: {abn_res['EntityName']}")
                st.write(f"{abn_res['AbnStatus']} since {abn_res['AbnStatusEffectiveFrom']}")
            elif abn_res['AbnStatus']=='Cancelled':
                st.warning('This is a valid ABN but cancelled')
                st.write(f"Entity Name: {abn_res['EntityName']}")
                st.write(f"{abn_res['AbnStatus']} since {abn_res['AbnStatusEffectiveFrom']}")
            else:
                st.error('Invalid ABN')

    st.subheader("Contact and Client Info:")
    with st.container(border=True):
        clientsig_firstname = st.text_input('Contact First Name')
        clientsig_lastname = st.text_input('Contact Last Name')
        clientsig_position = st.text_input('Contact Position')
        client_compname = st.text_input('Client Name',value=f"{abn_res['EntityName']}")
        client_shortname = st.text_input('Client Short Name')
        # client_abn = st.text_input('Client ABN')
        client_address1 = st.text_input('Client Address1')
        client_address2 = st.text_input('Client Address2')
        clientsig_fullname = f"{clientsig_firstname} {clientsig_lastname}"


with c2:
    #### Services offered selections
    st.subheader("Services:")
    with st.container(border=True):
        ita = st.checkbox("Indirect Tax Analysis")
        lta= st.checkbox("Land Tax Analysis")
        aas = st.checkbox("Assurance and Advisory Services")

    ### 1. Indirect Tax Analysis ###        
    if ita:
        ita_ind = ""
        selected_ita_lta.append("Indirect Tax Analysis")
        ### If Inderect Tax Analysis is selected Tax Scopes selection activates ###
        st.subheader("Tax Scopes")
        with st.container(border=True):
            if st.checkbox("GST"):
                selected_ts.append("GST")
            if st.checkbox("FTC"):
                selected_ts.append("FTC")
            ### If GST is included in the selection add specific line ####
            if 'GST' in selected_ts:
                with_gst = ", general ledger GST account reconciliations and GST returns"
                
    tax_scope = ' and '.join(selected_ts)
    if len(selected_ts)==0:
        encompassing = ''
        tax_scope2 = 'GST,FTC'
    else:
        encompassing = ' encompassing '
        tax_scope2 = ','.join(selected_ts)
    ### 2. Land Tax Analysis ###
    if lta:
        lta_ind = ""
        selected_ita_lta.append("Land Tax Analysis")
        
    #### 1-2 Indirect Tax and Land tax
    ### Title for Section 2: Indirect Tax Only or Land Tax Only or Both
    ita_lta_title = ' and '.join(selected_ita_lta)
    if len(selected_ita_lta)>0:
        il_ind = ""
    if ita_lta_title == "Land Tax Analysis":
        lta_sec_ind = ""
        il_word = "land"


    ### 3. Assurance and Advisory Services
    if aas:
        aas_ind = ""
        ### If Assurance and Advisory Services is selected Scopes selection activates ###
        st.subheader("Assurance and Advisory Scopes")
        with st.container(border=True):
            ### sub item 1
            idt = st.checkbox("Independent data testing")

            ### sub item 2
            if st.checkbox("RFI Response Review"):
                rfi_ind = ""
                selected_aas.append({'desc':['Reviewing the first Request for Information (RFI)',"AUD$"]})

            ### sub item 3
            if st.checkbox("Drafting a Central GST Guide"):
                draft_ind = ""
                selected_aas.append({'desc':['Drafting a Central GST Guide',"AUD$"]})

        if idt:
            test_ind = ""
            st.subheader("Test Categories")
            with st.container(border=True):
                ### Sub item 1.1-3
                selected_test_cat = st.radio("Test Categories",options=["Accounts Payable (AP) only",
                                                                        "Accounts Receivable (AR) only",
                                                                        "Full data testing"],label_visibility='hidden')

                if selected_test_cat == "Accounts Payable (AP) only":
                    ap_ar = "AP"
                elif selected_test_cat == "Accounts Receivable (AR) only":
                    ap_ar = "AR"
                else:
                    ap_ar = "AP, AR"
            selected_aas.append({'desc':[f'Independent Data Testing ({selected_test_cat})',"AUD$"]})

ca = st.toggle("With Confidentiality Agreement")

if ca:
    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])
    ca_date = st.date_input("Agreement Date")
    ca_monthyear = ca_date.strftime('%B %Y')
    ca_day = ordinal(ca_date.day)
    agreement_date = f"{ca_day} of {ca_monthyear}"
            
if st.button("Process"):
    if (aas) & (len(selected_aas)==0):
        st.error("Please select 1 or more Assurance and Advisory scope")
    else:
        doc = DocxTemplate('BTG EL.docx')
        context = {
            "clientsig_firstname":clientsig_firstname
            ,"clientsig_fullname":clientsig_fullname
            ,"clientsig_position":clientsig_position
            ,"client_compname":client_compname
            ,"client_shortname":client_shortname
            ,"client_abn":abn
            ,"client_address1":client_address1
            ,"client_address2":client_address2
            ,"tax_scope":tax_scope
            ,"tax_scope2":tax_scope2
            ,"encompassing":encompassing
            ,"with_gst":with_gst
            ,"test_categories":selected_test_cat
            ,"ap_ar":ap_ar
            ,"ita_ind":ita_ind
            ,"lta_ind":lta_ind
            ,"il_ind":il_ind
            ,"aas_ind":aas_ind
            ,"colname":colname
            ,"selected_aas":selected_aas
            ,"test_ind":test_ind
            ,"rfi_ind":rfi_ind
            ,"draft_ind":draft_ind
            ,"ita_lta_title":ita_lta_title
            ,"lta_sec_ind":lta_sec_ind
            ,"il_word":il_word
        }

        doc.render(context)

        lines = doc.paragraphs
        for line in lines:
            #delete empty lines with to_delete
            if  "to_delete" in line.text:
                delete_paragraph(line)

        if not aas:
            Delete_table(doc,0)
        
        doc.save(f'BTG Engagement Letter.docx')

        if ca:
            doc2 = DocxTemplate('BTG - CA.docx')
            context2 = {
                "agreement_date":agreement_date
                ,"client_compname":client_compname
                ,"client_abn":abn
                ,"clientsig_fullname":clientsig_fullname
            }
            doc2.render(context2)
            doc2.save(f'BTG Confidentiality Agreement.docx')

            zip_file_name = f'BTG Engagement Letter - {client_compname}.zip'

            with zipfile.ZipFile(zip_file_name, 'w') as zipf:
                for file in ['BTG Engagement Letter.docx','BTG Confidentiality Agreement.docx']:
                    zipf.write(file)
            
            with open(zip_file_name, "rb") as file:
                st.download_button(
                    label="Download EL with Confidentiality",
                    data=file,
                    key=zip_file_name,
                    file_name=zip_file_name,
                    )
                    # if os.path.exists(zip_file_name):
                    #     os.remove(zip_file_name)
        else:
            with open(f'BTG Engagement Letter.docx', 'rb') as f:
                st.download_button('Download Letter', f, file_name=f'BTG Engagement Letter - {client_compname}.docx')