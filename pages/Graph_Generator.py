import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import math

st.set_page_config(layout='wide', initial_sidebar_state='expanded')

file = st.file_uploader("Upload Testing Report")

if file is not None:

    ap = pd.read_excel(file ,sheet_name="AP")
    ar = pd.read_excel(file,sheet_name="AR")

    cols = ['Data Population','Exception Identified', 'Accuracy Rate']

    ap[cols] = ap[cols].apply(pd.to_numeric,errors='coerce',axis=1)
    ar[cols] = ar[cols].apply(pd.to_numeric,errors='coerce',axis=1)

    ap_final = ap[~ap["Data Population"].isna()].copy()
    ar_final = ar[~ar["Data Population"].isna()].copy()

    ap_final["Accuracy Rates"] = ap_final["Accuracy Rate"].apply(lambda x : str(round(x*100,2))+"%")
    ar_final["Accuracy Rates"] = ar_final["Accuracy Rate"].apply(lambda x : str(round(x*100,2))+"%")

    ap_accy = ap_final[["Code","Accuracy Rates"]].T
    ap_accy.columns = ap_accy.iloc[0]
    ap_accy.drop(index=ap_accy.index[0], axis=0, inplace=True)
    # ap_accy.reset_index(inplace=True)

    # st.dataframe(ap_accy)

    vertical = 3
    horizontal = math.ceil(len(ap_final)/3)

#################################################################

    st.header("Option 1")
    ap_fig = make_subplots(specs=[[{"secondary_y": True}]])

    ap_fig.add_trace(go.Bar(
            x=ap_final["Code"],
            y=ap_final["Data Population"],
            name="Population",
            marker_color="#1c2544",
            text=ap_final["Data Population"],
            texttemplate='%{text:,}',
            offsetgroup=1
                ),
            secondary_y=False,
            )

    ap_fig.add_trace(go.Bar(
            x=ap_final["Code"],
            y=ap_final["Exception Identified"],
            name="Exception Identified",
            marker_color="#7DECFF",
            text=ap_final["Exception Identified"],
            texttemplate='%{text:,}',
            offsetgroup=2
                ),
            secondary_y=True,
            )


    ap_fig.update_layout(

        legend=dict(yanchor="top", y=-.2, xanchor="left", x=0.4),
        template="plotly_white",
        title="BTG - Accounts Payable Testing"
    )
    ap_fig.update_yaxes(secondary_y=False, showgrid=False,title="Population",)
    ap_fig.update_yaxes(secondary_y=True, showgrid=False,title="Exception",)

    st.plotly_chart(ap_fig,theme="streamlit",use_container_width=True)


    ar_fig = make_subplots(specs=[[{"secondary_y": True}]])

    ar_fig.add_trace(go.Bar(
            x=ar_final["Code"],
            y=ar_final["Data Population"],
            name="Population",
            yaxis="y1",
            offsetgroup=0,
            marker_color="#1c2544",
            text=ar_final["Data Population"],
            texttemplate='%{text:,}'
                ),
            secondary_y=False,
            )

    ar_fig.add_trace(go.Bar(
            x=ar_final["Code"],
            y=ar_final["Exception Identified"],
            name="Exception Identified",
            yaxis="y2",
            offsetgroup=1,
            marker_color="#7DECFF",
            text=ar_final["Exception Identified"],
            texttemplate='%{text:,}'
                ),
            secondary_y=True,
            )
    ar_fig.update_layout(

        legend=dict(yanchor="top", y=-.2, xanchor="left", x=0.4),
        template="plotly_white",
        title="BTG - Accounts Receivable Testing"
    )
    ar_fig.update_yaxes(secondary_y=False, showgrid=False,title="Population",)
    ar_fig.update_yaxes(secondary_y=True, showgrid=False,title="Exception",)

    st.plotly_chart(ar_fig,theme="streamlit",use_container_width=True)


##############################################################################################


    st.header("Option 2")
    
    ap_fig2 = go.Figure()

    ap_fig2.add_trace(go.Bar(
            x=ap_final["Code"],
            y=ap_final["Data Population"],
            name="Population",
            yaxis="y1",
            offsetgroup=0,
            marker_color="#1c2544",
            text=ap_final["Data Population"],
            texttemplate='%{text:,}'
                )
            )

    ap_fig2.add_trace(go.Bar(
            x=ap_final["Code"],
            y=ap_final["Exception Identified"],
            name="Exception Identified",
            yaxis="y2",
            offsetgroup=1,
            marker_color="#7DECFF",
            text=ap_final["Exception Identified"],
            texttemplate='%{text:,}'
                )
            )
    
    ap_fig2.add_trace(go.Scatter(
            x=ap_final["Code"], 
            y=ap_final["Accuracy Rate"], 
            name="Accuracy Rate",
            text=ap_final["Accuracy Rates"],
            textposition="top right",
            mode="markers+text",
            marker_color="#8b7955",
            marker_symbol="diamond",
            marker_size=10,
            yaxis="y3",
            ))




    ap_fig2.update_layout(

        yaxis=dict(
            title="Population",
            titlefont=dict(
                color="#1c2544"
            ),
            tickfont=dict(
                color="#1c2544"
            ),
            showgrid=False
        ),
        

        yaxis2=dict(
            title="Exception",
            titlefont=dict(
                color="#5676A5"
            ),
            tickfont=dict(
                color="#5676A5"
            ),
            anchor="x",     # specifying x - axis has to be the fixed
            overlaying="y",  # specifyinfg y - axis has to be separated
            side="right",  # specifying the side the axis should be present
            showgrid=False
        ),
        
        yaxis3=dict(

            visible=False,
            
            anchor="free",  # specifying x - axis has to be the fixed
            overlaying="y",  # specifyinfg y - axis has to be separated
            side="right",  # specifying the side the axis should be present
            position=0,
            range = [0,1.1],
            showgrid=False
        ),
        
        legend=dict(yanchor="top", y=-.2, xanchor="left", x=0.4),
        template="plotly_white",
        title="BTG - Accounts Payable Testing"
    )

    st.plotly_chart(ap_fig2,theme="streamlit",use_container_width=True)


    ar_fig2 = go.Figure()

    ar_fig2.add_trace(go.Bar(
            x=ar_final["Code"],
            y=ar_final["Data Population"],
            name="Population",
            yaxis="y1",
            offsetgroup=0,
            marker_color="#1c2544",
            text=ar_final["Data Population"],
            texttemplate='%{text:,}'
                )
            )

    ar_fig2.add_trace(go.Bar(
            x=ar_final["Code"],
            y=ar_final["Exception Identified"],
            name="Exception Identified",
            yaxis="y2",
            offsetgroup=1,
            marker_color="#7DECFF",
            text=ar_final["Exception Identified"],
            texttemplate='%{text:,}'
                )
            )
    

    ar_fig2.add_trace(go.Scatter(
            x=ar_final["Code"], 
            y=ar_final["Accuracy Rate"], 
            name="Accuracy Rate",
            text=ar_final["Accuracy Rates"],
            textposition="top right",
            mode="markers+text",
            marker_color="#8b7955",
            marker_symbol="diamond",
            marker_size=10,
            yaxis="y3",
            ))




    ar_fig2.update_layout(
        yaxis=dict(
            title="Population",
            titlefont=dict(
                color="#1c2544"
            ),
            tickfont=dict(
                color="#1c2544"
            ),
            showgrid=False
        ),

        yaxis2=dict(
            title="Exception",
            titlefont=dict(
                color="#5676A5"
            ),
            tickfont=dict(
                color="#5676A5"
            ),
            anchor="x",     # specifying x - axis has to be the fixed
            overlaying="y",  # specifyinfg y - axis has to be separated
            side="right",  # specifying the side the axis should be present
            showgrid=False
        ),
        
        yaxis3=dict(

            visible=False,
            
            anchor="free",  # specifying x - axis has to be the fixed
            overlaying="y",  # specifyinfg y - axis has to be separated
            side="right",  # specifying the side the axis should be present
            position=0,
            range = [0,1.1],
            showgrid=False
        
        ),
        
        legend=dict(yanchor="top", y=-.2, xanchor="left", x=0.4),
        template="plotly_white",
        title="BTG - Accounts Receivable Testing"
    )

    st.plotly_chart(ar_fig2,theme="streamlit",use_container_width=True)

########################################################################

    st.header("Option 3")

    ap_fig3 = go.Figure()

    ap_fig3.add_trace(go.Bar(
            x=ap_final["Code"],
            y=ap_final["Data Population"],
            name="Population",
            yaxis="y1",
            offsetgroup=0,
            marker_color="#1c2544",
            text=ap_final["Data Population"],
            texttemplate='%{text:,}'
                )
            )

    ap_fig3.add_trace(go.Bar(
            x=ap_final["Code"],
            y=ap_final["Exception Identified"],
            name="Exception Identified",
            yaxis="y2",
            offsetgroup=1,
            marker_color="#7DECFF",
            text=ap_final["Exception Identified"],
            texttemplate='%{text:,}'
                )
            )
    
    ap_fig3.add_trace(
        go.Table(
            name = "Accuracy Rate",
            header = dict(values=list(ap_accy.columns),
                          fill_color = '#8b7955',
                          font = dict(color = 'white')
                          ),
            cells = dict(values=[ap_accy[f"{column}"] for column in list(ap_accy.columns)],
                         fill_color='#DFFAFF',
                         font = dict(color = '#1c2544'),
                         align='center'),
            domain = dict(x=[0, 1],y=[0, 0.38])
                    ),
    )


    ap_fig3.update_layout(

        xaxis1 =dict(dict(domain=[0, 1], 
                         anchor='x'),
                    visible = False,
                    ),

        yaxis=dict(
            dict(domain=[0.4,1]),
            title="Population",
            titlefont=dict(
                color="#1c2544"
            ),
            tickfont=dict(
                color="#1c2544"
            ),
            showgrid=False,
            
        ),
        

        yaxis2=dict(
            dict(domain=[0.4,1]),
            title="Exception",
            titlefont=dict(
                color="#5676A5"
            ),
            tickfont=dict(
                color="#5676A5"
            ),
            anchor="x",     # specifying x - axis has to be the fixed
            overlaying="y",  # specifyinfg y - axis has to be separated
            side="right",  # specifying the side the axis should be present
            showgrid=False,
    
        ),
        
        
        showlegend=False,
        template="plotly_white",
        title="BTG - Accounts Payable Testing"
    )

    st.plotly_chart(ap_fig3,theme="streamlit",use_container_width=True)


    
    ar_fig3 = go.Figure()

    ar_fig3.add_trace(go.Bar(
            x=ar_final["Code"],
            y=ar_final["Data Population"],
            name="Population",
            yaxis="y1",
            offsetgroup=0,
            marker_color="#1c2544",
            text=ar_final["Data Population"],
            texttemplate='%{text:,}'
                )
            )

    ar_fig3.add_trace(go.Bar(
            x=ar_final["Code"],
            y=ar_final["Exception Identified"],
            name="Exception Identified",
            yaxis="y2",
            offsetgroup=1,
            marker_color="#7DECFF",
            text=ar_final["Exception Identified"],
            texttemplate='%{text:,}'
                )
            )
    
    ar_fig3.add_trace(
        go.Table(
            name = "Accuracy Rate",
            header = dict(values=list(ap_accy.columns),
                          fill_color = '#8b7955',
                          font = dict(color = 'white')
                          ),
            cells = dict(values=[ap_accy[f"{column}"] for column in list(ap_accy.columns)],
                         fill_color='#DFFAFF',
                         font = dict(color = '#1c2544'),
                         align='center'),
            domain = dict(x=[0, 1],y=[0, .38])
                    ),
    )


    ar_fig3.update_layout(

        xaxis1=dict(dict(domain=[0, 1], anchor='x'),
                    visible = False,),

        yaxis=dict(
            dict(domain=[0.4,1]),
            title="Population",
            titlefont=dict(
                color="#1c2544"
            ),
            tickfont=dict(
                color="#1c2544"
            ),
            showgrid=False,
            
        ),
        

        yaxis2=dict(
            dict(domain=[0.4,1]),
            title="Exception",
            titlefont=dict(
                color="#5676A5"
            ),
            tickfont=dict(
                color="#5676A5"
            ),
            anchor="x",     # specifying x - axis has to be the fixed
            overlaying="y",  # specifyinfg y - axis has to be separated
            side="right",  # specifying the side the axis should be present
            showgrid=False
        ),
        
        
        # legend=dict(yanchor="top", y=0, xanchor="left", x=0),
        showlegend=False,
        template="plotly_white",
        title="BTG - Accounts Payable Testing"
    )

    st.plotly_chart(ar_fig3,theme="streamlit",use_container_width=True)