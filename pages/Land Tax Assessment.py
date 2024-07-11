import streamlit as st
from PIL import Image
import os
import google.generativeai as genai
from dotenv import load_dotenv
import tempfile
from pathlib import Path
import fitz  # PyMuPDF
from io import BytesIO
import pandas as pd
import re

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def load_prompt():
    input_prompt = """
                   You are a land tax advisor with an expertise in understanding invoices and land tax reports and documents.
                   You will receive input images as invoices, financial document with tables &
                   you will have to answer questions based on the input image.
                   If you don't know the answer, please refrain from speculating.
                   """
    return input_prompt

def generate_response_llm(input_question, prompt, image):
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    response = model.generate_content([input_question, prompt, image])
    return response.text

def convert_pdf_to_images(pdf_data):
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp:
        temp.write(pdf_data)
        temp_path = temp.name

    images = []
    with tempfile.TemporaryDirectory() as temp_dir:
        doc = fitz.open(temp_path)
        last_page_num = len(doc) - 1  # Get the last page number
        page = doc.load_page(last_page_num)  # Load only the last page
        pix = page.get_pixmap(dpi=170)
        img_temp_path = Path(temp_dir) / f"page_{last_page_num}.jpg"
        pix.save(str(img_temp_path), jpg_quality=98)
        img_data = img_temp_path.read_bytes()
        images.append(img_data)

    return images

def parse_table_from_response(response_text):
    # Parse markdown table from response
    pattern = r"\|.*?\|"
    table = []
    for line in response_text.split("\n"):
        if re.match(pattern, line):
            table.append([cell.strip() for cell in line.split("|")[1:-1]])
    if table:
        columns = table[0]
        data = table[1:]
        df = pd.DataFrame(data, columns=columns)
        return df
    return pd.DataFrame()

def remove_invalid_rows(df):
    # Ensure 'Filename' is the first column
    cols = ['Filename'] + [col for col in df.columns if col != 'Filename']
    df = df[cols]
    
    # Remove rows where the second column contains '---' or ':---'
    df = df.loc[~df.iloc[:, 1].str.contains(r"^---$|^:---$", na=False)]
    
    # Reset the index
    df.reset_index(drop=True, inplace=True)
    
    return df

def main():
    st.set_page_config(page_title="AI Land Tax Assessment Extractor")

    st.title("AI Land Tax Assessment Extractor")

    # Initialize session state for the input prompt
    if "input_prompt" not in st.session_state:
        st.session_state.input_prompt = ""

    user_question = st.text_input("Input prompt", value=st.session_state.input_prompt, key="input")

    st.sidebar.title("Invoice File")

    # Button to set the input prompt
    # if st.sidebar.button("Sample Prompt 1"):
    #     st.session_state.input_prompt = "Please parse all the information on the invoice."
    #     st.experimental_rerun()

    if st.sidebar.button("Sample Prompt 1"):
        st.session_state.input_prompt = "Please parse the name, correspondence ID, client ID, issue date, aggregated taxable land value, less threshold, Total tax payable and then get all the details for all records on the aggregated land table and get the Land item number, Land Item and property ID, % owned, Land Tax Taxable Value, Surcharge Taxable Value, Average land value and Land values for each year (rename the column like so Land value 2017, Land value 2018 and so on) and put them on a single table (values on the table can be repeated per row and upcase all column names)."
        st.experimental_rerun()

    uploaded_files = st.sidebar.file_uploader("Choose files...", type=["pdf", "jpg", "png", "jpeg"], accept_multiple_files=True)

    all_images = []
    filenames = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            filenames.append(uploaded_file.name)
            file_extension = uploaded_file.name.split(".")[-1].lower()
            if file_extension == "pdf":
                pdf_data = uploaded_file.read()
                images_data = convert_pdf_to_images(pdf_data)
                all_images.extend(images_data)
            else:
                image = Image.open(uploaded_file)
                img_byte_arr = BytesIO()
                image.save(img_byte_arr, format='JPEG')
                all_images.append(img_byte_arr.getvalue())

    prompt = load_prompt()

    if st.button("Send"):
        combined_df = pd.DataFrame()
        with st.spinner("Start processing..."):
            for img_data, filename in zip(all_images, filenames):
                image = Image.open(BytesIO(img_data))
                response = generate_response_llm(input_question=user_question, image=image, prompt=prompt)
                df = parse_table_from_response(response)
                if not df.empty:
                    df['Filename'] = filename  # Add filename to each row
                    combined_df = pd.concat([combined_df, df], ignore_index=True)

        combined_df = remove_invalid_rows(combined_df)

        if not combined_df.empty:
            st.subheader("Response:")
            st.dataframe(combined_df)

if __name__ == "__main__":
    main()
