# !pip3 install fitz
# !pip3 install PyMuPDF
from ftplib import FTP_TLS
import streamlit as st
import pandas as pd
import smtplib
import ftplib
import os
import re
import base64
from io import StringIO, BytesIO
import zipfile
import glob
import fitz
import pandas as pd



st.set_page_config(
    page_title="PDF Merger",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


def merger(file,filename):
    with zipfile.ZipFile(file,"r") as zip_ref:
        zip_ref.extractall(filename.split('.')[0])
 
    result = fitz.open()
    files = glob.glob(f"{filename.split('.')[0]}/**.pdf")   
    df = pd.DataFrame(files, columns=['file'])    
    try:
        df['ref'] = df['file'].apply(lambda f :  int(f.split('/')[-1].split(". ")[0]) )
    except Exception as e:
        print(f'Invalid Reference Number for file {f}')
        raise e
    
    for i,f in df.sort_values('ref').iterrows():
        doc = fitz.open(f['file'])
        ref_num = f['ref']
    
        for page in doc:
            page.clean_contents(False)
            rect = fitz.Rect(5, 5, 150, 22)   # rectangle (left, top, right, bottom) in pixels
    
            text = f"""  BTG Reference: {ref_num}"""
            page.draw_rect(rect, color=(0,0,1))
            rc = page.insert_textbox(rect, text, color=(0, 0, 1))
    
        result.insert_pdf(doc)

    result.save("result.pdf")       


################################################################################################################
st.title('📗 PDF Merger')
st.caption('Merge multiple PDF files into one.')
file = st.file_uploader(label=f"Upload Invoices in Zip",
                                        type="zip",
                                        accept_multiple_files=False)



# st.write(file)    
# st.write(file.name)

# file = "Archive.zip"


submitted = st.button("Process")
if submitted and file is not None:
    with st.spinner("Processing"):
        df = merger(file,file.name)
        with open("result.pdf", "rb") as pdf_file:
            PDFbyte = pdf_file.read()

        st.download_button(label="Download Merge PDF",
                            data=PDFbyte,
                            file_name="Consolidated.pdf",
                            mime='application/octet-stream')
    
elif submitted and file is None:
    st.error("No file uploaded!!!")

 

