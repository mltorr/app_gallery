import streamlit as st
from PIL import Image
import pytesseract
import numpy as np
import fitz
import re
import pandas as pd
import tempfile
import base64
from io import BytesIO

def generate_excel_download_link(df):
    towrite = BytesIO()
    df.to_excel(towrite, index=False, header=True)
    towrite.seek(0) 
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="BAS Lodge.xlsx">Download BAS Lodge.xlsx</a>'
    return st.markdown(href, unsafe_allow_html=True)

def read_values(pdf_data):
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
        temp.write(pdf_data)
        temp_path = temp.name

    with tempfile.NamedTemporaryFile(suffix='.png') as img_temp:
        doc = fitz.open(temp_path)
        page = doc.load_page(0)
        pix = page.get_pixmap(dpi=300)
        pix.save(img_temp.name, jpg_quality=98)
        doc.close()

        img1 = np.array(Image.open(img_temp.name))
        text = pytesseract.image_to_string(img1, config='--psm 6')
        
        # Define regex patterns for each line
        patterns = {
            "1B Owed by ATO": r'.*1B.*Owed.*y.*ATO(.*)',
            "1A Owed to ATO": r'.*1A.*Owed.*o.*ATO(.*)',
            "G1 Total sales": r'.*G1.*otal.*sales(.*)',
            "G2 Export sales": r'.*G2.*xport.*sales(.*)',
            "G3 Other GST-free sales": r'.*G3.*ther.*GST.*sales(.*)',
            "G10 Capital purchases": r'.*G10.*apital.*purchases(.*)',
            "G11 Non-capital purchases": r'.*Non.*purchases(.*)',
            "7A Deferred imports amount": r'.*Deferred.*imports(.*)',

        }

        values = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_match = re.search(r'\$\.*(.*)', match.group(1))
                values[key] = value_match.group(1) if value_match else ''

        return values

st.title("BAS Lodge Scan PDF")
up = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)

if st.button("Upload"):
    data_list = []
    columns = ["PDF File"]
    total_files = len(up)
    progress = st.progress(0)

    for i, file in enumerate(up):
        pdf_data = file.read()
        print(f"Currently processing: {file.name}")
        values = read_values(pdf_data)

        if values:
            new_columns = list(values.keys())
            # Extend the columns list only with new columns not already present
            columns.extend(col for col in new_columns if col not in columns)
            data_list.append([file.name] + [values.get(col, '') for col in columns[1:]])

        progress.progress((i + 1) / total_files)
    
    progress.empty()  # Remove progress bar
    if data_list:
        df = pd.DataFrame(data_list, columns=columns)
        st.success("Here's the extracted info:")
        st.dataframe(df)
        generate_excel_download_link(df)
