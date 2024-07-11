# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: env
#     language: python
#     name: python3
# ---

# %%
import streamlit as st
from PIL import Image
import pytesseract
import numpy as np
import fitz
import re 
import tempfile
import pandas as pd
import time
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode, DataReturnMode
from annotated_text import annotated_text
import base64
from ftplib import FTP_TLS
import ftplib
import utils

utils.setup_page("Keword Lookup")

# %%
st.set_page_config(layout="wide")

# %%
def displayPDF(file):
    # Opening file from file path
    # with open(file, "rb") as f:
    #     base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="900" height="1000" type="application/pdf">'

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

def onehub_login():
    host = "ftp.onehub.com"
    port = 2022
    usr = "brian.desagun@btgi.com.au"
    pwd = "Sidelinework!527"
    ftps = FTP_TLS()
    ftps.connect(host, port)
    ftps.login(usr, pwd)

    return ftps

# %%
st.title('Invoice Keyword Lookup')

# %%
if 'key' not in st.session_state:
    st.session_state['key'] = pd.DataFrame()

# %%
keywords_input = st.text_input('Lookup keywords', placeholder='Type all keywords separated by ;')
ignore_case = st.checkbox('Ignore case',value=True)


# %%
source = st.radio(
        "Select file source 👇",
        [ "🗂 File Upload", "🌐 OneHub Folder"],
        key="visibility",
    )

if source == "🗂 File Upload":
    uploaded_files = st.file_uploader("Upload PDF files", type=['pdf'], accept_multiple_files=True)

elif source == "🌐 OneHub Folder":

        with st.spinner('Fetching OneHub Folders'):
            if 'ws' not in st.session_state:
                clients = onehub_login().nlst('Internal/Invoice Keyword Lookup/Clients/')
                clients.remove('001')
                st.session_state['ws'] = clients

            ws = st.selectbox('Client Folder', st.session_state['ws'])

            ohpath = st.text_input(
                "Folder Path", placeholder='sample/folder/path', key='ohpath')    
            st.caption('Access is restricted to the Clients folder in the Internal OneHub workspace.')

# %%
st.markdown(
"""<style>
.keyword_h { background-color:yellow   ; 
            color:grey;
            border-radius: 10px;
            padding: 3px;
}
</style>
""", unsafe_allow_html=True)

# %% [markdown]
# st.markdown("""
#             <span class="keyword_h">test</span>
#             """, unsafe_allow_html=True)
# annotated_text(
#     "This ",
#     ("is", ""),
#     " some ",
#     ("annotated", ""),
#     ("text", ""),
#     " for those of ",
#     ("you", ""),
#     " who ",
#     ("like", ""),
#     " this sort of ",
#     ("thing", ""),
#     "."
# )

# %%
# annotated_text(r"""Anglicare Nell Slade Respite Centre BOOKS
# 593 Old Northern Road,
# Glenhaven, NSW 2156 9 May 2019
# Dear Esther,
# PO: NSR-002943
# <span class="keyword_h">INVOICE</span> for the May 2019 session of Armchair Traveller's Club at Nell Slade Respite
# Centre.
# Thursday 9 May 2019 = $160 sr 16) Unclaimed <span class="keyword_h">GST</span> of $16.00
# Total = $176 inc. <span class="keyword_h">GST</span>.
# <span class="keyword_h">PLEASE</span> credit this amount to the following business bank account:
# Bank: St George Bank, Kogarah NSW,
# Account name: Good Walking Books,
# BSB: 112-879
# Account number: 055725121
# Yours sincerely,
# Almis Simans
# GOOD WALKING BOOKS / ABN: 90321534832 / T:0400 502339
# """
# )
if st.button('Start Process'):
    keywords = [i.strip() for i in keywords_input.split(";") if i !='']
    if 0 in (len(uploaded_files), len(keywords)):
        st.warning('Missing/Invalid lookup keywords or pdf files', icon="⚠️")
        
    else:
        # Process all pdf files

        # progress_text = "Operation in progress. Please wait."
        # my_bar = st.progress(0, text=progress_text)

        # for percent_complete in range(100):
        #     time.sleep(0.1)
        #     my_bar.progress(percent_complete + 1, text=progress_text)

        latest_iteration = st.empty()
        bar = st.progress(0)
        out_list = []
        for i in range(len(uploaded_files)):

            file = uploaded_files[i]
            bytes_data = file.read()
            
            # Change progress bar value and label
            latest_iteration.text(f'Processing {file.name}')
            bar.progress((100//len(uploaded_files))*i)


            # Process te PDF File
            doc = fitz.open(stream=bytes_data,  filetype="pdf")


            with tempfile.NamedTemporaryFile(suffix='.jpg') as temp:
                page_num = 0
                for page in doc:  
                    file_dict = {}
                    file_dict['file'] = file.name
                    
                    latest_iteration.text(f'Processing {file.name} : Reading file')
                    # page = doc.load_page(0)  # number of page
                    pix = page.get_pixmap(dpi=300)

                    pix.save(temp.name, jpg_quality=98)


                    img1 = np.array(Image.open(temp.name))
                    text = pytesseract.image_to_string(img1, config='--psm 6')



                    file_dict['page'] = page_num + 1
                    text_trimmed = re.sub(' +', ' ',text) # Remove duplicate spaces
                    case_mod  = r"(?i)" if ignore_case else "" # case sensitive/insensitive

                    for keyword in keywords:
                        latest_iteration.text(f'Processing {file.name} : finding {keyword}')
                        regex_pattern = case_mod + r".*\b"  + keyword + r"\b.*"
                        file_dict[keyword] = len(re.findall(regex_pattern, text_trimmed))

                        text_trimmed = re.sub(case_mod +  r'\b' + keyword + r'\b' ,'<span class="keyword_h">' + keyword.upper() + '</span>' ,text_trimmed) # Remove duplicate spaces

                    
                    file_dict['text'] = text_trimmed
                    file_dict['id'] = i
                    # print(text_trimmed)
                    out_list.append(file_dict)
                    page_num +=1
            
            doc.close() 
            
        bar.progress(100) 
        latest_iteration.text(f'Complete')
        df_out = pd.DataFrame(out_list)



        st.session_state['key'] = df_out

        # st.dataframe(df_out)
        # with st.form("my_form"):

        # select the columns you want the users to see
df_out = st.session_state['key']        
# all_cols = list(df_out.columns)

# %%
if df_out.shape[0] > 0:
    st.header('Results:')
    display_cols = list(df_out.columns)
    display_cols.remove('text')
    display_cols.remove('id')

    gb = GridOptionsBuilder.from_dataframe(df_out[display_cols])
    # configure selection
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    gb.configure_side_bar()
    gridOptions = gb.build()

    data = AgGrid(df_out,
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
                allow_unsafe_jscode=True,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
                
                # reload_data = True,
                # data_return_mode = DataReturnMode.AS_INPUT,
                # update_mode = GridUpdateMode.MODEL_CHANGED,
                )
    selected_rows = data["selected_rows"]
    
    if len(selected_rows) != 0:
        col1, col2 = st.columns([1,2])
        with col1:
            # selected_row_idx = selected_rows[0]['_selectedRowNodeInfo']['nodeRowIndex']
            st.write(selected_rows[0]['text'], unsafe_allow_html=True)


        
        # st.markdown(f":orange[{selected_rows[0]}]")
        # st.markdown(f":orange[{selected_row_idx}]")


        with col2:
            file = uploaded_files[selected_rows[0]['id']]
            # bytes_data = file.read()
            displayPDF(file)
            # st.markdown(bytes_data)

    
    # st.markdown(f":orange[{selected_rows[0].index}]")
            
            # submitted = st.form_submit_button("Submit")
            # if submitted:
            #     st.write('test')


        # @st.cache_data
        # def convert_df(df):
        #     # IMPORTANT: Cache the conversion to prevent computation on every rerun
        #     return df.to_csv().encode('utf-8')

        # csv = convert_df(df_out)

        # st.download_button(
        #     label="Download data as CSV",
        #     data=csv,
        #     file_name='Invoice Lookup.csv',
        #     mime='text/csv',
        # )

# %%

