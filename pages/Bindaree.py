import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import streamlit.components.v1 as components
import utils

utils.setup_page("Bindaree")

# st.set_page_config(layout='wide', initial_sidebar_state='expanded')


####################### FUNCTIONS #######################

def year_change():
    # Month Update
    st.session_state.month_options = df.loc[df['YearStr']==st.session_state.year_selected,'MonthName'].unique().tolist()

    # Group Update
    ps = datetime.strptime(str(st.session_state.year_selected)+str(st.session_state.month_selected),"%Y%B")
    groups = df_group.loc[(~df_group["GST Group"].isna()) &
                          (df_group['Valid From']<=ps) &
                          (df_group['Valid To']>=ps),'GST Group'].unique().tolist()
    st.session_state.group_options = groups

    #Entity Update
    entities = df.loc[(df['Grouped']!="Y")&
                  (df['YearStr']==st.session_state.year_selected)&
                  (df['MonthName']==st.session_state.month_selected),'Entity'].unique().tolist()
    ex_entities = []
    if len(st.session_state.group_selected) == 0:
       st.session_state.entity_options = entities
    else: 
        for group in st.session_state.group_selected:
            ent = df_group.loc[df_group["GST Group"]==group,"Entities"].values[0].split(',')
            ex_entities.extend(ent)
        st.session_state.entity_options = list(set(entities)-set(ex_entities))
    

def month_change():
    #Group Update
    ps = datetime.strptime(str(st.session_state.year_selected)+str(st.session_state.month_selected),"%Y%B")
    groups = df_group.loc[(~df_group["GST Group"].isna()) &
                          (df_group['Valid From']<=ps) &
                          (df_group['Valid To']>=ps),'GST Group'].unique().tolist()
    st.session_state.group_options = groups

    #Entity Update
    entities = df.loc[(df['Grouped']!="Y")&
                  (df['YearStr']==st.session_state.year_selected)&
                  (df['MonthName']==st.session_state.month_selected),'Entity'].unique().tolist()
    ex_entities = []
    if len(st.session_state.group_selected) == 0:
       st.session_state.entity_options = entities
    else: 
        for group in st.session_state.group_selected:
            ent = df_group.loc[df_group["GST Group"]==group,"Entities"].values[0].split(',')
            ex_entities.extend(ent)
        st.session_state.entity_options = list(set(entities)-set(ex_entities))

def group_change():
    #Entity Update
    entities = df.loc[(df['Grouped']!="Y")&
                  (df['YearStr']==st.session_state.year_selected)&
                  (df['MonthName']==st.session_state.month_selected),'Entity'].unique().tolist()
    ex_entities = []
    if len(st.session_state.group_selected) == 0:
       st.session_state.entity_options = entities
    else: 
        for group in st.session_state.group_selected:
            ent = df_group.loc[df_group["GST Group"]==group,"Entities"].values[0].split(',')
            ex_entities.extend(ent)
        st.session_state.entity_options = list(set(entities)-set(ex_entities))


####################### END FUNCTIONS #######################


####################### STYLE #######################
# st.markdown(
#     """
#     <style>
#         css-j7qwjs e1fqkh3o7 {display: none;}
#     </style>
#     """,unsafe_allow_html=True
# )

# # CSS to inject contained in a string
# hide_table_row_index = """
#         <style>
#         thead tr th:first-child {display:none}
#         tbody th {display:none}
#         </style>
#         """

# # Inject CSS with Markdown
# st.markdown(hide_table_row_index, unsafe_allow_html=True)


with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


####################### END STYLE #######################


####################### LOAD DATA #######################
df = pd.read_excel("Bindaree Data.xlsx")
df['Period'] = df['Date'].dt.strftime("%b%Y")
df['YearStr'] = df['Date'].dt.strftime("%Y")
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['MonthName'] = df['Date'].dt.strftime("%B")
df["link"] = df["Client"].astype(str)+"|"+df["Entity"].astype(str)+"|"+df["Period"].astype(str)
df["Bas Code"] = df["Bas Code"].astype(str)

df_group = pd.read_excel("groupings.xlsx",sheet_name="groups")

months_index = {'January' : 0,
                 'February' : 1,
                 'March' : 2 ,
                 'April' : 3,
                 'May' : 4,
                 'June' : 5,
                 'July' : 6,
                 'August' : 7,
                 'September' : 8,
                 'October' : 9,
                 'November' : 10,
                 'December' : 11}

####################### END LOAD DATA #######################


####################### SIDE BAR #######################
st.sidebar.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 0 26px; border-bottom:1px solid #cecece; width:100%;">
                </span>
''', unsafe_allow_html=True)
st.sidebar.markdown(f'Latest Period : `{max(df["Date"]).strftime("%B %Y")}`')
st.sidebar.markdown(f'Earliest Period : `{min(df["Date"]).strftime("%B %Y")}`')
st.sidebar.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 0 26px; border-bottom:1px solid #cecece; width:100%;">
                </span>
''', unsafe_allow_html=True)


#Year Options
if 'year_options' not in st.session_state:
    st.session_state.year_options = sorted(df['YearStr'].unique().tolist(),reverse=True)


y,m = st.sidebar.columns(2)
with y:
   year_selected = y.selectbox("Year",
                               st.session_state.year_options,
                               key='year_selected',
                               index=0,
                               on_change=year_change
                               )
# Month Options
if 'month_options' not in st.session_state:
    st.session_state.month_options = df.loc[df['YearStr']==st.session_state.year_selected,'MonthName'].unique().tolist()


with m:
   month_selected = m.selectbox("Month",
                                st.session_state.month_options,
                                key='month_selected',
                                index=months_index[max(df["Date"]).strftime("%B")],
                                on_change=month_change
                                )

# Periods
period_selected = datetime.strptime(str(st.session_state.year_selected)+str(st.session_state.month_selected),"%Y%B")
previous_month = datetime(period_selected.year,period_selected.month-1,1) if period_selected.month != 1 else datetime(period_selected.year-1,12,1)
previous_year = datetime.strptime(str(int(year_selected)-1)+str(month_selected),"%Y%B")
last12months = period_selected + relativedelta(months=-11)

MonthName = pd.date_range(last12months,period_selected,freq='MS').strftime("%B").tolist()

lastfouryears = [str(int(year_selected)-3),str(int(year_selected)-2),str(int(year_selected)-1),year_selected]

#Group Options
if 'group_options' not in st.session_state:
    groups = df_group.loc[(~df_group["GST Group"].isna()) &
                          (df_group['Valid From']<=period_selected) &
                          (df_group['Valid To']>=period_selected),'GST Group'].unique().tolist()
    st.session_state.group_options = groups

   
st.sidebar.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 0 26px; border-bottom:1px solid #cecece; width:100%;">
                </span>
''', unsafe_allow_html=True)

group_selected = st.sidebar.multiselect("Group",
                                      st.session_state.group_options,
                                      key='group_selected',
                                      on_change=group_change)

#Entity Options

if 'entity_options' not in st.session_state:
    entities = df.loc[(df['Grouped']!="Y")&
                  (df['YearStr']==st.session_state.year_selected)&
                  (df['MonthName']==st.session_state.month_selected),'Entity'].unique().tolist()
    ex_entities = []
    if len(st.session_state.group_selected) == 0:
       st.session_state.entity_options = entities
    else:
        for group in st.session_state.group_selected:
            ent = df_group.loc[df_group["GST Group"]==group,"Entities"].values[0].split(',')
            ex_entities.extend(ent)
        st.session_state.entity_options = list(set(entities)-set(ex_entities))


st.sidebar.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 0 26px; border-bottom:1px solid #cecece; width:100%;">
                </span>
''', unsafe_allow_html=True)

entity_selected = st.sidebar.multiselect("Entities",
                                      st.session_state.entity_options,
                                      key='entity_selected'
                                      )

st.sidebar.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 0 26px; border-bottom:1px solid #cecece; width:100%;">
                </span>
''', unsafe_allow_html=True)

entities_final = [*group_selected,*entity_selected]


####################### END SIDE BAR #######################

####################### TITLE #######################
st.markdown(f'''<h1 style="color:#294C89; font-weight:bold; margin:0;font-size:45px;">Bindaree Beef Dashboard </h1>
                <p style="font-style:italic; margin:0;font-size:20px;">GST Filing Period : {month_selected} {year_selected}</p>
                <span style="display:inline-block; vertical-align:middle; margin:0 0 26px; border-bottom:1px solid #cecece; width:100%;">
                </span>
                <p><br></p>
''', unsafe_allow_html=True)


####################### CARDS #######################

def metrics(bas_code):
    amount_selected = "{:,.2f}".format(round(df[(df['Bas Code'].isin(bas_code))&
                        (df['Date']==period_selected)&
                        (df["Entity"].isin(entities_final))]['Amount'].sum(),2))
    amount_prev_month = "{:,.2f}".format(round(df[(df['Bas Code'].isin(bas_code))&
                        (df['Date']==previous_month)&
                        (df["Entity"].isin(entities_final))]['Amount'].sum(),2))
    amount_prev_year = "{:,.2f}".format(round(df[(df['Bas Code'].isin(bas_code))&
                        (df['Date']==previous_year)&
                        (df["Entity"].isin(entities_final))]['Amount'].sum(),2))

    if int(float(amount_prev_month.replace(',', ''))) == 0:
        amount_delta_prev_month = ""
    else:
        amount_delta_prev_month = "{:,.2f}%".format((abs(float(amount_selected.replace(',', '')))-abs(float(amount_prev_month.replace(',', ''))))/abs(float(amount_prev_month.replace(',', ''))))


    if int(float(amount_prev_year.replace(',', ''))) == 0:
        amount_delta_prev_year = ""
    else:
        amount_delta_prev_year = "{:,.2f}%".format((abs(float(amount_selected.replace(',', '')))-abs(float(amount_prev_year.replace(',', ''))))/abs(float(amount_prev_year.replace(',', ''))))

    if amount_prev_month > amount_selected:
        color_prev_month = "Red"
        icon_prev_month = "⬇"
    else:
        color_prev_month = "Green"
        icon_prev_month = "⬆"

    if amount_prev_year > amount_selected:
        color_prev_year = "Red"
        icon_prev_year = "⬇"
    else:
        color_prev_year = "Green"
        icon_prev_year = "⬆"


    return amount_selected, amount_prev_month, amount_prev_year, amount_delta_prev_month,amount_delta_prev_year,color_prev_month,color_prev_year,icon_prev_month,icon_prev_year


# # arrow_up = ⬆️⬆⬇

c1,c2,c3,c4 = st.columns(4)

net_gst = "NET GST REFUND" if df[(df['Bas Code'].isin(["1"]))&(df['Date']==period_selected)&(df["Entity"].isin(entities_final))]['Amount'].sum() > 0 else "NET GST PAYABLE"

cards_pos = {c1 : [['G1'],"TOTAL SALES"],
             c2 : [['G10','G11'],"TOTAL PURCHASES"],
             c3 : [["1"],net_gst],
             c4 : [["7"],"FUEL TAX CREDIT"]
            }

for i in cards_pos:
    with i:
        amount_selected, amount_prev_month, amount_prev_year, amount_delta_prev_month,amount_delta_prev_year,color_prev_month,color_prev_year,icon_prev_month,icon_prev_year = metrics(cards_pos[i][0])
        components.html(f'''
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        <div class="card" style="width: 100%;">
            <div class="card-body"">
                <h5 class="card-subtitle text-muted" style="font-size:1rem;font-weight: bold;">{cards_pos[i][1]}</h5>
                <p></p>
                <h6 class="card-title mb-2" style="font-size:1.25rem;">{amount_selected}</h6>
                <p class="card-text" style="font-size: .6rem;">Prev Month: {amount_prev_month} <span style="color:{color_prev_month}">{amount_delta_prev_month} {icon_prev_month}</span></p>
                <p class="card-text" style="font-size: .6rem;">Prev Year: {amount_prev_year} <span style="color:{color_prev_year}">{amount_delta_prev_year} {icon_prev_year}</span></p>
            </div>
        </div>
        ''',height=200)    

####################### END CARDS #######################


####################### TABLE AND BAR CHARTS #######################

## Filter only by Date
st.header("Summary Amount per Entity")
st.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 0 26px; border-bottom:1px solid #cecece; width:100%;">
                </span>
''', unsafe_allow_html=True)
bas_item_selected = st.selectbox("BAS Item",df['Bas Category'].unique().tolist())
df_basItem_selected = df[(df['Date']==period_selected)&
                        (df['Bas Category']==bas_item_selected)&
                        (df['Grouped']!="Y")].groupby(["Client","Entity","Bas Category","Bas Code","Period"])[["Amount"]].sum().reset_index().sort_values("Amount",ascending=False)

df_basItem_selected2 = df_basItem_selected.sort_values("Amount",ascending=True)

tbc1, tbc2 = st.columns([1.5,1])

with tbc1:
    st.title("")
    st.dataframe(df_basItem_selected)

with tbc2:
    figbar = px.bar(df_basItem_selected2, 
                    x='Amount', 
                    y='Entity',
                    orientation='h'
    )

    for axis in figbar.layout:
        if type(figbar.layout[axis]) == go.layout.XAxis:
            figbar.layout[axis].title.text = ''
        if type(figbar.layout[axis]) == go.layout.YAxis:
            figbar.layout[axis].title.text = ''

    figbar.update_traces(
            hovertemplate = "<b>Amount</b> : $%{x:,.2f}<br><b>Entity</b> : %{y}"
            )
    
    st.plotly_chart(figbar,theme="streamlit",use_container_width=True)


####################### END TABLE AND BAR CHARTS #######################


####################### SALES #######################
st.header("SALES")
st.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 0 26px; border-bottom:1px solid #cecece; width:100%;">
                </span>
''', unsafe_allow_html=True)

df_sales = df[(df["Entity"].isin(entities_final))].sort_values(by="Date").copy()

bas_codes = {"G2":"Export",
            "G3":"GST-Free",
            "G4":"Input-Taxed",
            "G8":"Taxable"}

df_sales["BAS Item"] = df_sales["Bas Code"].map(bas_codes)



def bas_items_ch():
    if len(st.session_state.sales_basitem)>0:
        st.session_state.turnover = False

def gst_turnover_ch():
    if st.session_state.turnover:
        st.session_state.sales_basitem = []



s1,s2,s3 = st.columns([1,2,2])
s1,s2,s3,s4 = st.columns(4)

with s1:
    sales_charttype = st.radio("Chart Type: ",["Bar","Line"],horizontal=True)

with s2:
    bas_items = st.multiselect("BAS Items",["Export","GST-Free","Input-Taxed","Taxable"],key="sales_basitem",on_change=bas_items_ch)
    
with s2:
    gst_turnover = st.checkbox("GST Turn-over",key="turnover",on_change=gst_turnover_ch)


st.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 10% 10px; border-bottom:1px solid #cecece; width:80%;">
                </span>
''', unsafe_allow_html=True)



if gst_turnover:
    df_turnover_g1 = df_sales[(df_sales["Bas Code"]=="G1")&
                        (df_sales["Date"]>=last12months)&
                        (df_sales["Date"]<=period_selected)].groupby(["link","Entity","Date","Period"],dropna=False).agg(G1=("Amount","sum")).reset_index()
    df_turnover_g9 = df_sales[(df_sales["Bas Code"]=="G9")&
                        (df_sales["Date"]>=last12months)&
                        (df_sales["Date"]<=period_selected)].groupby(["link"],dropna=False).agg(G9=("Amount","sum")).reset_index()
    df_turnover = df_turnover_g1.merge(df_turnover_g9,on="link",how="outer")
    df_turnover["Turnover"] = df_turnover["G1"]-df_turnover["G9"]
    df_turnover.sort_values(by="Date",inplace=True)

    total_turnover = "{:,}".format(round(df_turnover["Turnover"].sum(),2))

    components.html(f'''
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        <div style="width: 100%;">
            <div class="card-body">
                <h5 class="card-subtitle text-muted" style="font-size:1rem;font-weight: bold;">Total GST Turnover</h5>
                <p></p>
                <h6 class="card-title mb-2" style="font-size:1.25rem;">{total_turnover}</h6>
            </div>
        </div>
        ''',height=100)    
    
    # Line Chart
    if sales_charttype == "Line":
        fig = px.line(df_turnover, 
                    x="Period", 
                    y="Turnover",
                    markers=True,
                    title=f'Trend Analysis by GST Turnover')
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.XAxis:
                fig.layout[axis].title.text = ''
        st.plotly_chart(fig,theme="streamlit",use_container_width=True)

    # BAr Chart
    if sales_charttype == "Bar":
        fig = px.bar(df_turnover, 
                    x="Period", 
                    y="Turnover",
                    title=f'Trend Analysis by GST Turnover')
        for axis in fig.layout:
            if type(fig.layout[axis]) == go.layout.XAxis:
                fig.layout[axis].title.text = ''
        st.plotly_chart(fig,theme="streamlit",use_container_width=True)

else:

    with s3:
        fouryears = st.multiselect(f"For the year ending {month_selected}: ",lastfouryears)
    df_sales["RPeriod"] = np.select(
                            condlist=[(df_sales["Date"]>=period_selected + relativedelta(months=-47))&(df_sales["Date"]<=period_selected + relativedelta(years=-3)),
                                      (df_sales["Date"]>=period_selected + relativedelta(months=-35))&(df_sales["Date"]<=period_selected + relativedelta(years=-2)),
                                      (df_sales["Date"]>=period_selected + relativedelta(months=-23))&(df_sales["Date"]<=period_selected + relativedelta(years=-1)),
                                      (df_sales["Date"]>=last12months)&(df_sales["Date"]<=period_selected)],
                            choicelist=lastfouryears,
                            default=None
                            )
    df_sales_basitems = df_sales[(df_sales["RPeriod"].isin(fouryears))&
                                 (df_sales["BAS Item"].isin(bas_items))].groupby(["MonthName","RPeriod","Date"],dropna=False)["Amount"].sum().reset_index()

    df_sales_basitems .sort_values(by="Date",inplace=True)

    # Line Chart
    if sales_charttype == "Line":
        fig2 = px.line(df_sales_basitems, 
                        x="MonthName", 
                        y="Amount",
                        color="RPeriod",
                        title=f'Trend Analysis',
                        category_orders={"MonthName": MonthName})
        for axis in fig2.layout:
            if type(fig2.layout[axis]) == go.layout.XAxis:
                fig2.layout[axis].title.text = ''
        
        fig2.update_layout(
        legend_title=f"For the year ending {month_selected}"
    )
        fig2.update_traces(
            hovertemplate = "<b>Month</b> : %{x}<br><b>Amount</b> : $%{y:,.2f}"
        )
        st.plotly_chart(fig2,theme="streamlit",use_container_width=True)


    # BAr Chart
    if sales_charttype == "Bar":
        fig2 = px.bar(df_sales_basitems, 
                        x="MonthName", 
                        y="Amount",
                        color="RPeriod",
                        barmode="group",
                        title=f'Trend Analysis',
                        category_orders={"MonthName": MonthName})
        for axis in fig2.layout:
            if type(fig2.layout[axis]) == go.layout.XAxis:
                fig2.layout[axis].title.text = ''
        
        fig2.update_layout(
        legend_title=f"For the year ending {month_selected}"
    )
        fig2.update_traces(
            hovertemplate = "<b>Month</b> : %{x}<br><b>Amount</b> : $%{y:,.2f}"
        )
        st.plotly_chart(fig2,theme="streamlit",use_container_width=True)

####################### END SALES #######################



# ####################### PURCHASE #######################
st.header("PURCHASE")
st.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 0 26px; border-bottom:1px solid #cecece; width:100%;">
                </span>
''', unsafe_allow_html=True)

df_purchase = df[(df["Entity"].isin(entities_final))].sort_values(by="Date").copy()

bas_codes2 = {"G15":"Private",
            "G14":"GST-Free",
            "G13":"Input-Taxed",
            "G19":"Taxable"}

df_purchase["BAS Item"] = df_purchase["Bas Code"].map(bas_codes2)


p1,p2,p3 = st.columns([1,1.8,2])

with p1:
    purchase_charttype = st.radio("Chart Type: ",["Bar","Line"],horizontal=True,key="p_chartype")

with p2:
    p_bas_items = st.multiselect("BAS Items",["Export","GST-Free","Input-Taxed","Taxable"])

with p3:
    p_fouryears = st.multiselect(f"For the year ending {month_selected}: ",lastfouryears,key="p_fouryears")
    


st.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 10% 10px; border-bottom:1px solid #cecece; width:80%;">
                </span>
''', unsafe_allow_html=True)


df_purchase["RPeriod"] = np.select(
                        condlist=[(df_purchase["Date"]>=period_selected + relativedelta(months=-47))&(df_purchase["Date"]<=period_selected + relativedelta(years=-3)),
                                    (df_purchase["Date"]>=period_selected + relativedelta(months=-35))&(df_purchase["Date"]<=period_selected + relativedelta(years=-2)),
                                    (df_purchase["Date"]>=period_selected + relativedelta(months=-23))&(df_purchase["Date"]<=period_selected + relativedelta(years=-1)),
                                    (df_purchase["Date"]>=last12months)&(df_purchase["Date"]<=period_selected)],
                        choicelist=lastfouryears,
                        default=None
                        )
df_purchase_basitems = df_purchase[(df_purchase["RPeriod"].isin(p_fouryears))&
                                (df_purchase["BAS Item"].isin(p_bas_items))].groupby(["MonthName","RPeriod","Date"],dropna=False)["Amount"].sum().reset_index()

df_purchase_basitems.sort_values(by="Date",inplace=True)

# st.write(MonthName)
# Line Chart
if purchase_charttype == "Line":
    p_fig2 = px.line(df_purchase_basitems, 
                    x="MonthName", 
                    y="Amount",
                    color="RPeriod",
                    title=f'Trend Analysis',
                    category_orders={"MonthName": MonthName})
    for axis in p_fig2.layout:
        if type(p_fig2.layout[axis]) == go.layout.XAxis:
            p_fig2.layout[axis].title.text = ''
    
    p_fig2.update_layout(
    legend_title=f"For the year ending {month_selected}"
)
    p_fig2.update_traces(
                hovertemplate = "<b>Month</b> : %{x}<br><b>Amount</b> : $%{y:,.2f}"
            )
    st.plotly_chart(p_fig2,theme="streamlit",use_container_width=True)


# BAr Chart
if purchase_charttype == "Bar":
    p_fig2 = px.bar(df_purchase_basitems, 
                    x="MonthName", 
                    y="Amount",
                    color="RPeriod",
                    barmode="group",
                    title=f'Trend Analysis',
                    category_orders={"MonthName": MonthName})
    for axis in p_fig2.layout:
        if type(p_fig2.layout[axis]) == go.layout.XAxis:
            p_fig2.layout[axis].title.text = ''
    
    p_fig2.update_layout(
    legend_title=f"For the year ending {month_selected}"
)
    p_fig2.update_traces(
                hovertemplate = "<b>Month</b> : %{x}<br><b>Amount</b> : $%{y:,.2f}"
            )
    st.plotly_chart(p_fig2,theme="streamlit",use_container_width=True)

# ####################### END PURCHASE #######################


# ####################### TAXES #######################
st.header("TAXES")
st.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 0 26px; border-bottom:1px solid #cecece; width:100%;">
                </span>
''', unsafe_allow_html=True)

df_tax = df[(df["Entity"].isin(entities_final))].sort_values(by="Date").copy()

bas_codes3 = {"G9":"GST Payable",
            "G20":"GST Receivable",
            "1":"Net GST",
            "7":"FTC"}

df_tax["BAS Item"] = df_tax["Bas Code"].map(bas_codes3)



t1,t2,t3 = st.columns(3)

with t1:
    data_attr = st.radio("Data Attribute:",["GST items","Year trend"],key="data_attribute",horizontal=True)

if data_attr == "GST items":
    with t2:
        tax_bas_items = st.multiselect("BAS items:",["GST Payable","GST Receivable","Net GST","FTC"],key="tax_bas_items")
    tax_year_selected = [str(int(year_selected))]
    t_color = "BAS Item"
    t_legend_title=f"BAS Items"
else:
    with t2:
        tax_bas_items = [st.selectbox("BAS items:",["GST Payable","GST Receivable","Net GST","FTC"],key="tax_bas_items")]
    with t3:
        tax_year_selected = st.multiselect("For the year ending:",lastfouryears)
    t_color = "RPeriod"
    t_legend_title=f"For the year ending {month_selected}"

df_tax["RPeriod"] = np.select(
                        condlist=[(df_tax["Date"]>=period_selected + relativedelta(months=-47))&(df_tax["Date"]<=period_selected + relativedelta(years=-3)),
                                    (df_tax["Date"]>=period_selected + relativedelta(months=-35))&(df_tax["Date"]<=period_selected + relativedelta(years=-2)),
                                    (df_tax["Date"]>=period_selected + relativedelta(months=-23))&(df_tax["Date"]<=period_selected + relativedelta(years=-1)),
                                    (df_tax["Date"]>=last12months)&(df_tax["Date"]<=period_selected)],
                        choicelist=lastfouryears,
                        default=None
                        )


df_tax_basitems = df_tax[(df_tax["RPeriod"].isin(tax_year_selected))&
                                (df_tax["BAS Item"].isin(tax_bas_items))].groupby(["MonthName","RPeriod","Date","BAS Item"],dropna=False)["Amount"].sum().reset_index()

df_tax_basitems.sort_values(by="Date",inplace=True)


st.markdown(f'''<span style="display:inline-block; vertical-align:middle; margin:0 10% 10px; border-bottom:1px solid #cecece; width:80%;">
            </span>
''', unsafe_allow_html=True)


t_fig2 = px.line(df_tax_basitems, 
                x="MonthName", 
                y="Amount",
                color=t_color,
                title=f'Trend Analysis',
                category_orders={"MonthName": MonthName})
for axis in t_fig2.layout:
    if type(t_fig2.layout[axis]) == go.layout.XAxis:
        t_fig2.layout[axis].title.text = ''

t_fig2.update_layout(
legend_title=t_legend_title
)

t_fig2.update_traces(
            hovertemplate = "<b>Month</b> : %{x}<br><b>Amount</b> : $%{y:,.2f}"
        )
st.plotly_chart(t_fig2,theme="streamlit",use_container_width=True)

# if data_attr == "Year trend":
#     t_df = df_tax_basitems.groupby(["RPeriod"])["Amount"].sum().reset_index()
#     t_df.sort_values(by="RPeriod")
#     t_df["prev"] = t_df["Amount"].shift(1)
#     t_df["diff"] = t_df["Amount"].astype(float) - t_df["prev"].astype(float)
#     t_df[" "] = t_df["diff"].apply(lambda x : "🟢" if x > 0 else "🔻" if x < 0 else None)
#     # t_df.drop(columns=["prev","diff"],inplace=True)
#     st.write(t_df)

# ####################### END TAXES #######################

