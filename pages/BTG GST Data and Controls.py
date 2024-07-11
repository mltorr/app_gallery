from docxtpl import DocxTemplate
import streamlit as st
import os


#Variables
    #full_client_name
    #client_short_name
    #start_date
    #end_date
    #full_entity_name_in_scope
    #ap_population_count
    #ap_accuracy_percentage
    #ar_population
    #ar_accuracy_percentage
    #client_erp_system


st.set_page_config(
    page_title="BTG GST Data and Controls Testing",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

def submit():
    st.session_state.submitted = True

with st.form("parameters"):
    full_client_name = st.text_input("Full Client Name")
    full_entity_name_in_scope = st.text_input("Full Entity Name in Scope")
    client_short_name = st.text_input("Client Short Name")
    client_erp_system = st.text_input("Client ERP System")
    start_date = st.date_input("Review Start Date").strftime("%d %B %Y")
    end_date = st.date_input("Review End Date").strftime("%d %B %Y")
    ap_population_count = str(st.number_input("AP Population count",min_value=0,step=1))
    ap_accuracy_percentage = str(st.number_input("AP Accuracy %",min_value=0.00,max_value=100.00,step=.01))
    ar_population = str(st.number_input("AR Population count",min_value=0,step=1))
    ar_accuracy_percentage = str(st.number_input("AR Accuracy %",min_value=0.00,max_value=100.00,step=.01))
    submit = st.form_submit_button("Process",on_click=submit)


if st.session_state.submitted:
    doc = DocxTemplate('BTG GST Data and Controls Testing_Template.docx')

    context = {"full_client_name":full_client_name,
            "full_entity_name_in_scope":full_entity_name_in_scope,
            "client_short_name":client_short_name,
            "client_erp_system":client_erp_system,
            "start_date":start_date,
            "end_date":end_date,
            "ap_population_count":ap_population_count,
            "ap_accuracy_percentage":ap_accuracy_percentage,
            "ar_population":ar_population,
            "ar_accuracy_percentage":ar_accuracy_percentage
            }

    with st.spinner("Processing ..."):
        doc.render(context)
        doc.save(f'{client_short_name} BTG GST Data and Controls.docx')

        with open(f'{client_short_name} BTG GST Data and Controls.docx','rb') as f:
            download = st.download_button("Download Report",
                            f,
                            mime="docx",
                            file_name=f'{client_short_name} BTG GST Data and Controls.docx')
            if download:
                os.remove(f'{client_short_name} BTG GST Data and Controls.docx')

            

                
