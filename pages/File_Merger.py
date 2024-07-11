# from ftplib import FTP_TLS
import streamlit as st
import pandas as pd
import smtplib
# import ftplib
import os
import re
import base64
from io import StringIO, BytesIO
import utils

utils.setup_page("File Merger")


# st.set_page_config(
#     page_title="File Merger",
#     page_icon="favicon.png",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

with st.sidebar:
    # st.title("File Merger")
    page = st.radio(
        "",
        ("Merge Files",
         "Custom File Format Request",
        #  "Feature Request"
         )
    )

@st.cache
def convert_df(df,sep):
    return df.to_csv(index=False,sep=sep).encode('utf-8')

def send_mail(message):
    mailserver = smtplib.SMTP('smtp.office365.com', 587)
    mailserver.ehlo()
    mailserver.starttls()
    mailserver.login('brian.desagun@btgi.com.au', 'Sidelinework!527')
    mailserver.sendmail('brian.desagun@btgi.com.au',
                        ['brian.desagun@btgi.com.au','jhunriel.btgi.com.au'], message)
    mailserver.quit()
    st.info("Request sent.")


# def onehub_login():
#     host = "ftp.onehub.com"
#     port = 2022
#     usr = "jhunriel.amigo@btgi.com.au"
#     pwd = "Btginternational12"
#     ftps = FTP_TLS()
#     ftps.connect(host, port)
#     ftps.login(usr, pwd)

#     return ftps

# def generate_excel_download_link(df):
#     towrite = BytesIO()
#     df.to_excel(towrite,
#                 # encoding="utf-8", 
#                 index=False, 
#                 header=True)  # write to BytesIO buffer
#     towrite.seek(0)  # reset pointer
#     b64 = base64.b64encode(towrite.read()).decode()
#     href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="Merge.xlsx">Download merge data</a>'
#     return st.markdown(href, unsafe_allow_html=True)

def merge_master():
    st.title('📗 File Merger')
    st.caption('Merge multiple Excel or CSV files into one.')

    # source = st.radio(
    #     "Select file source 👇",
    #     ["🗂 File Upload",
    #      "🌐 OneHub Folder"],
    #     key="visibility",
    # )
 ########################### FILE UPLOAD ################################################
    # if source == "🗂 File Upload":
    uploaded_files = st.file_uploader(label=f"Upload files",
                                        type=["xlsx","xls","csv","txt"],
                                        accept_multiple_files=True)

    if len(uploaded_files) > 0:
        ext =  uploaded_files[0].name.lower().split(".")[-1]
    
        if ext in ["xls","xlsx"]:
            sheet_name = st.text_input(
                'Sheet Name to merge', value='Sheet1', placeholder='Sheet1')
            skiprows = st.number_input(
                'Number of rows to skip', min_value=0, step=1)

            btn =  st.button("Merge")
            if btn:
                df_merge = pd.DataFrame()
                for uploaded_file in uploaded_files:
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=skiprows,engine='openpyxl')
                    st.write(uploaded_file.name,' no of records: ',len(df))
                    df_merge = pd.concat([df_merge,df])
                st.write('Merge No of Records: ',len(df_merge))
                # generate_excel_download_link(df_merge)
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Write each dataframe to a different worksheet.
                    df_merge.to_excel(writer, sheet_name='Sheet1', index=False)
                    # Close the Pandas Excel writer and output the Excel file to the buffer
                    writer.save()

                    download = st.download_button(
                        label="Download data as Excel",
                        data=buffer,
                        file_name='Merge.xlsx',
                        mime='application/vnd.ms-excel'
                    )

        elif ext == 'csv':
            skiprows = st.number_input(
                'Number of rows to skip', min_value=0, step=1)
            
            btn =  st.button("Merge")
            if btn:
                df_merge = pd.DataFrame()
                for uploaded_file in uploaded_files:
                    df = pd.read_csv(uploaded_file, skiprows=skiprows)
                    st.write(uploaded_file.name,' no of records: ',len(df))
                    df_merge = pd.concat([df_merge,df])
                st.write('Merge No of Records: ',len(df_merge))

                csv = convert_df(df_merge,",")
                st.download_button(
                                    label="Download merge data",
                                    data=csv,
                                    file_name='merge.csv',
                                    mime='text/csv',
                                )

        elif ext == 'txt':
            delim = st.text_input('Delimiter used?')
            skiprows = st.number_input(
                'Number of rows to skip', min_value=0, step=1)
            
            btn =  st.button("Merge")
            if btn:
                df_merge = pd.DataFrame()
                for uploaded_file in uploaded_files:
                    df = pd.read_csv(uploaded_file, skiprows=skiprows,delimiter=delim)
                    st.write(uploaded_file.name,' no of records: ',len(df))
                    df_merge = pd.concat([df_merge,df])
                st.write('Merge No of Records: ',len(df_merge))

                csv = convert_df(df_merge,delim)
                st.download_button(
                                    label="Download merge data",
                                    data=csv,
                                    file_name='merge.txt',
                                    mime='text/csv',
                                )
############################################# ONEHUB ########################################################
    # elif source == "🌐 OneHub Folder":

    #     with st.spinner('Fetching OneHub Workspaces'):
    #         if 'ws' not in st.session_state:
    #             st.session_state['ws'] = onehub_login().nlst('/')

    #         ws = st.selectbox('Workspace', st.session_state['ws'])

######################################### CUSTOM #########################################################
def custom_request():
    st.title('Custom File Format Request')
    st.caption(
        """Send a request to **Data Team** to help convert files not in stadard format.""")

    with st.form('request'):
        st.subheader('Standard Request Form')
        st.caption(
            """Please fill-up all fields.""")

        client = st.text_input("Client Name")
        source = st.selectbox('Data Souce', ['OneDrive', 'OneHub'])
        path = st.text_input("Folder Path")

        mes = st.text_area(
            "Message", "", placeholder="""Write all information about the file format and the request.\n(Turnaround time is within 24 hours)""")

        req = st.text_input("Requestor's Name")
        submitted = st.form_submit_button("Submit")

        if submitted:
            message = f"""Subject: FTC Custom Format Request

            Client : {client}
            Data Source : {source}
            Folder Path : {path}
            Message : {mes}
            Requestor : {req}
            
            """
            with st.spinner("Sending request"):
                send_mail(message)


if page == "Merge Files":
    merge_master()
elif page == "Custom File Format Request":
    custom_request()
# elif page == "Feature Request":
#     st.error('Function under development.. ')
