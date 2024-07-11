import streamlit as st
import pandas as pd
import numpy as np
import re
import requests
import json
import base64
from io import StringIO, BytesIO
import plotly_express as px
import utils

utils.setup_page("BTG - ABN Checker")

st.set_page_config(
    page_title="BTG - ABN Checker",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

def generate_excel_download_link(df, fname):
    towrite = BytesIO()
    df.to_excel(towrite, encoding="utf-8", index=False, header=True)  # write to BytesIO buffer
    towrite.seek(0)  # reset pointer
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{fname} - BTG.xlsx">Download {fname} - BTG.xlsx</a>'
    return st.markdown(href, unsafe_allow_html=True)

def abn_lookup(df, abn_header, url, gui, ctry):
    result = []
    df['ABN_'] = df[abn_header].str.replace(r"[^\w]", '', regex=True)
    df['ABN_'] = df['ABN_'].fillna('')
    abns = [x for x in set(df['ABN_']) if len(x) != 0]
    my_progress = st.progress(0)
    status = st.empty()
    for abn in abns:
        u = '{}abn={}&guid={}'.format(url, abn, gui)
        r = requests.get(u)
        data = r.text
        cleanse_data = re.sub(r'\(|\)|\bcallback\b', "", data)
        entry = json.loads(cleanse_data)
        entry['ABN_'] = abn
        result += [entry]
        pcnt = (len(result) / len(abns))
        my_progress.progress(pcnt)
        status.write(f"Processing {len(result)} of {len(abns)} : {round(pcnt * 100, 2)}% Details (ABN: {abn} , ABN Status: {entry['AbnStatus']} , Message: {entry['Message']})")
    df_ato = pd.DataFrame.from_dict(result)
    st.success("Successfully Processed", icon="✅")
    df_ato = df_ato[['ABN_', 'EntityName', 'AbnStatus', 'AbnStatusEffectiveFrom', 'Gst', 'Message']].rename(columns={
        'EntityName': 'Entity Name',
        'AbnStatusEffectiveFrom': 'ABN Status Effective From',
        'Gst': 'GST Registration'
    })
    df_final = df.merge(df_ato, how="left", on="ABN_")
    df_final['ABN Status'] = np.select([(df_final['ABN_'].isna()) | (df_final['ABN_'].str.len() == 0),
                                        df_final['Message'].str.len() > 0],
                                       ['No ABN', 'Invalid ABN'],
                                       df_final['AbnStatus'])
    if ctry:
        df_final['BTG Comment'] = np.select(
            [(df_final['ABN Status'] == 'Active') & (~df_final['GST Registration'].isna())
             , (df_final[ctry] != 'AU') & (df_final[ctry].str.len() != 0)
             , (df_final['ABN Status'] == 'Active') & (df_final['GST Registration'].isna())
             , df_final['ABN Status'] == 'Invalid ABN'
             , (df_final['ABN_'].isna() | (df_final['ABN_'].str.len() == 0))
             , df_final['ABN Status'] == 'Cancelled'
             ],
            ["OK"
                , "OK. Foreign"
                , "GST not registered. Need To Confirm"
                , "Need to confirm ABN"
                , "No ABN. Need to Insert"
                , "Update Vendor Master. Is the vendor operating under a new ABN?"],
            None
        )
    else:
        df_final['BTG Comment'] = np.select(
            [(df_final['ABN Status'] == 'Active') & (~df_final['GST Registration'].isna())
             , (df_final['ABN Status'] == 'Active') & (df_final['GST Registration'].isna())
             , df_final['ABN Status'] == 'Invalid ABN'
             , (df_final['ABN_'].isna() | (df_final['ABN_'].str.len() == 0))
             , df_final['ABN Status'] == 'Cancelled'
             ],
            ["OK"
                , "GST not registered. Need To Confirm"
                , "Need to confirm ABN"
                , "No ABN. Need to Insert"
                , "Update Vendor Master. Is the vendor operating under a new ABN?"],
            None
        )
    df_final = df_final.drop(columns=['ABN_', 'AbnStatus', 'Message'])
    return df_final

st.title("ABN Checker")

submit = False

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Upload Vendor master file here!")
    vendor_master = st.file_uploader("Upload Vendor master file here!",
                                     type=["xlsx", "xls", "csv", "txt"],
                                     label_visibility="hidden",
                                     accept_multiple_files=False)

with col2:
    if vendor_master is not None:
        st.markdown("##### Fill file info and mapping")
        fname = vendor_master.name.split(".")[0]
        ext = vendor_master.name.lower().split(".")[-1]
        if ext in ["xls", "xlsx"]:
            with st.form("Mapping form", clear_on_submit=False):
                abn = st.text_input(
                    "ABN", value='ABN'
                )
                country = st.text_input(
                    "Country", placeholder="Country"
                )
                sheet_name = st.text_input(
                    "Sheet Name", value="Sheet1"
                )
                skiprows = st.number_input(
                    'Number of rows to skip', min_value=0, step=1
                )
                submit = st.form_submit_button()

                if not abn:
                    st.error("Please input ABN mapping")

                if submit and abn:
                    df = pd.read_excel(vendor_master, engine="openpyxl", sheet_name=sheet_name, skiprows=skiprows, dtype=str)

        if ext == 'csv':
            with st.form("Mapping form"):
                abn = st.text_input(
                    "ABN", placeholder='ABN'
                )
                country = st.text_input(
                    "Country", placeholder="Country"
                )
                skiprows = st.number_input(
                    'Number of rows to skip', min_value=0, step=1
                )
                submit = st.form_submit_button()

                if not abn:
                    st.error("Please input ABN mapping")

                if submit and abn:
                    df = pd.read_csv(vendor_master, skiprows=skiprows, dtype=str)

        if ext == 'txt':
            with st.form("Mapping form"):
                abn = st.text_input(
                    "ABN", placeholder='ABN'
                )
                country = st.text_input(
                    "Country", placeholder="Country"
                )
                delim = st.text_input(
                    "Delimiter", placeholder="|"
                )
                skiprows = st.number_input(
                    'Number of rows to skip', min_value=0, step=1
                )
                submit = st.form_submit_button()

                if not abn:
                    st.error("Please input ABN mapping")

                if submit and abn:
                    df = pd.read_csv(vendor_master, skiprows=skiprows, sep=delim, dtype=str)

if submit and abn:
    st.markdown("### Client Vendor Master Details")
    st.dataframe(df)

    st.subheader("Processing look up to ATO Website")
    abn_check = abn_lookup(df, abn, st.secrets.url, st.secrets.gui, country)
    st.dataframe(abn_check)
    generate_excel_download_link(abn_check, fname)

    df_bar_status = abn_check.groupby(["ABN Status"]).agg(Count=("ABN Status", "count"))
    df_bar_comment = abn_check.groupby(["BTG Comment"]).agg(Count=("ABN Status", "count"))
    bar1, bar2 = st.columns(2)
    with bar1:
        fig_status = px.bar(df_bar_status,
                            x="Count",
                            y=df_bar_status.index,
                            orientation="h",
                            color_discrete_sequence=["#0083B8"] * len(df_bar_status),
                            template="plotly_white",
                            title="ABN Status Summary")
        st.plotly_chart(fig_status)
    with bar2:
        fig_comment = px.bar(df_bar_comment,
                             x="Count",
                             y=df_bar_comment.index,
                             orientation="h",
                             color_discrete_sequence=["#0083B8"] * len(df_bar_comment),
                             template="plotly_white",
                             title="BTG Comment Summary")
        st.plotly_chart(fig_comment)
