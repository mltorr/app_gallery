import streamlit as st
import pandas as pd
import numpy as np
from streamlit_option_menu import option_menu
from io import BytesIO
import xlsxwriter 


st.set_page_config(layout='wide',initial_sidebar_state='collapsed',)

def save_uploaded(uploadedfile,filename):
    with open(filename,'wb') as f:
        f.write(uploadedfile.getbuffer())

def generate_excel_download_link(vendor_df,customer_df):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as w:
        # Write each dataframe to a different worksheet.
        vendor_df.to_excel(w,sheet_name="Vendor List",index=False)
        customer_df.to_excel(w,sheet_name="Customer List",index=False)

        w.close()

        st.download_button(
        label="Download Updated Master List",
        data=buffer,
        file_name=f"Master Vendor and Customer List.xlsx",
        mime="application/vnd.ms-excel"
    )



def cleanse(working_files,vendor_master_file,entity):
    col_names = ['Date', 'Account', 'Reference', 'Details', 'Gross', 'GST', 'Net']
    bindaree_vendor = pd.DataFrame()
    bindaree_customer = pd.DataFrame()

    for working_file in working_files:
        df = pd.read_excel(working_file,sheet_name="GST Audit Report",skiprows=6,engine="openpyxl",usecols="A:G",names=col_names, converters={'Reference':str})
        df["id"] = df.reset_index().index
        df['DT'] = pd.to_datetime(df['Date'],format="%d/%m/%Y",errors='coerce')
        bas_type = df.loc[(df.Date.str.contains('\w').fillna(False))&
                                (df.DT.isna()),:].copy()
        bas_type_ids = bas_type.loc[~bas_type.Date.str.contains(r'(?i)total'),"id"].unique().tolist()
        bas_type_ids.append(max(df["id"]))
        df["GST Classification"] = ""
        for i in range(len(bas_type_ids)-1):
                df.loc[(df["id"]>=bas_type_ids[i])&
                    (df["id"]<=bas_type_ids[i+1]-1),"GST Classification"] = df.loc[df["id"]==bas_type_ids[i],'Date'].values.item()
                
        df_final = df.loc[(~df.DT.isna())&
                                (~df["Date"].isna())&
                                (df["GST Classification"].isin(['GST on Income', 'GST on Expenses', 'GST Free Income','GST Free Expenses','GST on Capital'])),:].copy()

        df_final["Vendor"] = df_final["Details"].astype(str).apply(lambda x : x.split(" - ")[0])
        df_final["Vendor"] = df_final["Details"].astype(str).apply(lambda x : x.split(" - ")[0])
        df_final["Item Description"] = df_final["Details"].astype(str).apply(lambda x : x.split(" - ")[-1])
        df_final["Client"] = entity
        df_final["Remarks"] = ""
        
        df_vendor = df_final.loc[df_final["GST Classification"].isin(['GST on Expenses','GST Free Expenses','GST on Capital']),["Vendor","GST Classification","Item Description","Remarks","Client"]].drop_duplicates()
        df_vendor.sort_values(by="Vendor",inplace=True)
        
        df_customer = df_final.loc[df_final["GST Classification"].isin(['GST on Income','GST Free Income']),["Vendor","GST Classification","Item Description","Remarks","Client"]].drop_duplicates().rename(columns={"Vendor":"Customer"})
        df_customer.sort_values(by="Customer",inplace=True)
        
        bindaree_vendor = pd.concat([bindaree_vendor,df_vendor])
        bindaree_customer= pd.concat([bindaree_customer,df_customer])
        
    vendor_master = pd.read_csv(vendor_master_file,dtype=str)
    vm = vendor_master[["*ContactName","TaxNumber"]].rename(columns={"*ContactName":"Vendor"}).drop_duplicates()
    vm_c = vendor_master[["*ContactName","TaxNumber"]].rename(columns={"*ContactName":"Customer"}).drop_duplicates()


    #add ABN
    bindaree_vendor_w_abn = bindaree_vendor.merge(vm,how="left",on="Vendor")
    bindaree_customer_w_abn = bindaree_customer.merge(vm_c,how="left",on="Customer")

    return bindaree_vendor_w_abn, bindaree_customer_w_abn


c1, c2 = st.columns([2,8])

with c1:
    op = option_menu(None, 
                    ["Bindaree"],
                    # icons=[ "list-task"],
                    menu_icon="cast", 
                    default_index=0, 
                    orientation="vertical",
                    styles={
                            "container": {"padding": "0!important", "background-color": "#fafafa"},
                            "icon": {"color": "orange", "font-size": "1rem"}, 
                            "nav-link": {"font-size": "1rem", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
                            "nav-link-selected": {"background-color": "#1c2544"},
                        }
                    )
    
if op == "Bindaree":
    with c2:
        st.subheader("Update Current Vendor Master")
        vm_current_file = st.file_uploader("Upload current vendor master:",accept_multiple_files=False,type="xlsx")
        u1,u2 = st.columns(2)
        with u1:
            st.subheader("Bindaree Beef")
            bb_files = st.file_uploader("Upload Bindaree Beef Files Here:",accept_multiple_files=True,type="xlsx")
            bb_vm = st.file_uploader("Upload updated Vendor Master for Bindaree Beef:",accept_multiple_files=False,type="csv")
        with u2:
            st.subheader("Bindaree Food")
            bf_files = st.file_uploader("Upload Bindaree Food Files Here:",accept_multiple_files=True,type="xlsx")
            bf_vm = st.file_uploader("Upload updated Vendor Master for Bindaree Food:",accept_multiple_files=False,type="csv")

        u3,u4 = st.columns(2)
        with u3:
            st.subheader("Sanger")
            s_files = st.file_uploader("Upload Sanger Files Here:",accept_multiple_files=True,type="xlsx")
            s_vm = st.file_uploader("Upload updated Vendor Master for Sanger:",accept_multiple_files=False,type="csv")

        with u4:
            st.subheader("Yolarno Beef")
            y_files = st.file_uploader("Upload Yolarno Files Here:",accept_multiple_files=True,type="xlsx")
            y_vm = st.file_uploader("Upload updated Vendor Master for Yolarno:",accept_multiple_files=False,type="csv")

        bindaree_list = [
             [bb_files,bb_vm,"Bindaree Beef"],
             [bf_files,bf_vm,"Bindaree Food"],
             [s_files,s_vm,"Sanger"],
             [y_files,y_vm,"Yolarno"]

        ]
        vendor_list = pd.DataFrame()
        customer_list = pd.DataFrame()

        if st.button("Process"):
            with st.spinner("Proccessing..."):
                for i in bindaree_list:
                    if i[1] is not None:
                        save_uploaded(i[1],f"{i[2]} Vendor Master.csv")
                        
                    else:
                        i[1] = f"{i[2]} Vendor Master.csv"
                

                    if len(i[0])>0:
                        bindaree_vendor_w_abn, bindaree_customer_w_abn = cleanse(i[0],i[1],i[2])

                        vendor_list = pd.concat([vendor_list,bindaree_vendor_w_abn])
                        customer_list = pd.concat([customer_list,bindaree_customer_w_abn])


            st.success('Done!')
            vendor_list.sort_values(by=["Vendor",'GST Classification',"Client"],inplace=True)
            vendor_list.drop_duplicates(inplace=True)

            customer_list.sort_values(by=["Customer",'GST Classification',"Client"],inplace=True)
            customer_list.drop_duplicates(inplace=True)

            vendor_list_current = pd.read_excel(vm_current_file,sheet_name="Vendor List")
            vendor_list_current.drop_duplicates(inplace=True)
            customer_list_current = pd.read_excel(vm_current_file,sheet_name="Customer List")
            customer_list_current.drop_duplicates(inplace=True)

            # vendor_list_current = pd.read_excel("Master Vendor and Customer List.xlsx",sheet_name="Vendor List")
            # customer_list_current = pd.read_excel("Master Vendor and Customer List.xlsx",sheet_name="Customer List")

            try:
                vendor_list_current.drop(columns=["Is New Item","GST Classification change","New GST Classification"],inplace=True)
                customer_list_current.drop(columns=["Is New Item","GST Classification change","New GST Classification"],inplace=True)
            except:
                pass
                

            #Check for new items

            vendor_list["link"] = vendor_list["Vendor"].astype(str).str.upper()+"-"+vendor_list["Client"].astype(str).str.upper()+"-"+vendor_list["Item Description"].astype(str).str.upper()
            vendor_list_current["link"] = vendor_list_current["Vendor"].astype(str).str.upper()+"-"+vendor_list_current["Client"].astype(str).str.upper()+"-"+vendor_list_current["Item Description"].astype(str).str.upper()

            new_vendor = vendor_list.merge(vendor_list_current[["link","GST Classification"]],
                              how="left",
                              on="link",
                              indicator=True)
            new_vendor["Is New Item"] = np.where(new_vendor["_merge"]=="left_only","Yes","No")
            new_vendor["GST Classification change"] = np.where((new_vendor["_merge"]=="both") & (new_vendor["GST Classification_x"].str.upper() != new_vendor["GST Classification_y"].str.upper()),"Yes","No")
            


            updated_classification = new_vendor.loc[new_vendor["GST Classification change"]=="Yes",['link',"GST Classification change","GST Classification_x"]]
            updated_classification.rename(columns={"GST Classification_x":"New GST Classification"},inplace=True)

            # st.write(updated_classification)


            new_vendor_filter = new_vendor[new_vendor["Is New Item"]=="Yes"].copy()
            new_vendor_filter.drop(columns=["_merge",'GST Classification_y','GST Classification change'],inplace=True)
            new_vendor_filter.rename(columns={'GST Classification_x':'GST Classification'},inplace=True)



            updated_vendor_list = pd.concat([vendor_list_current,new_vendor_filter])

            updated_vendor_list_final = updated_vendor_list.merge(updated_classification,
                                                                  how="left",
                                                                  on="link")
            
            updated_vendor_list_final.drop(columns=["link"],inplace=True)

            #Customer
            customer_list["link"] = customer_list["Customer"].astype(str).str.upper()+"-"+customer_list["Client"].astype(str).str.upper()+"-"+customer_list["Item Description"].astype(str).str.upper()
            customer_list_current["link"] = customer_list_current["Customer"].astype(str).str.upper()+"-"+customer_list_current["Client"].astype(str).str.upper()+"-"+customer_list_current["Item Description"].astype(str).str.upper()

            new_customer = customer_list.merge(customer_list_current[["link","GST Classification"]],
                              how="left",
                              on="link",
                              indicator=True)
            new_customer["Is New Item"] = np.where(new_customer["_merge"]=="left_only","Yes","No")
            new_customer["GST Classification change"] = np.where((new_customer["_merge"]=="both") & (new_customer["GST Classification_x"].str.upper() != new_customer["GST Classification_y"].str.upper()),"Yes","No")
            


            updated_classification = new_customer.loc[new_customer["GST Classification change"]=="Yes",['link',"GST Classification change","GST Classification_x"]]
            updated_classification.rename(columns={"GST Classification_x":"New GST Classification"},inplace=True)

            new_customer_filter = new_customer[new_customer["Is New Item"]=="Yes"].copy()
            new_customer_filter.drop(columns=["_merge",'GST Classification_y','GST Classification change'],inplace=True)
            new_customer_filter.rename(columns={'GST Classification_x':'GST Classification'},inplace=True)

            updated_customer_list = pd.concat([customer_list_current,new_customer_filter])
            updated_customer_list_final = updated_customer_list.merge(updated_classification,
                                                                  how="left",
                                                                  on="link")
            
            updated_customer_list_final.drop(columns=["link"],inplace=True)



            generate_excel_download_link(updated_vendor_list_final,updated_customer_list_final)
            

