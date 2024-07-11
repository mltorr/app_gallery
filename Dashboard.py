import streamlit as st
import pandas as pd
import os
import imgkit
import base64
from pathlib import Path
import utils
import subprocess


utils.setup_page("Home")
# Read CSV
@st.cache_data()
def get_data():
    df = pd.read_csv("source.csv")
    df.sort_values(by='Category', inplace=True)
    return df

df=get_data()
# Function to generate and cache screenshots
@st.cache_data()
def generate_screenshot(url, name):
    screenshot_path = f"images/{name}.png"
    
    if not os.path.exists(screenshot_path):
        options = {
            '--crop-h': '600',
            '--format': 'png',
            '--enable-javascript': None,
            # 'javascript-delay': '10000',
            '--width': '800',
            '--height': '600',
        }
        imgkit.from_url(url, screenshot_path, options=options)
    
    return screenshot_path

# Function to convert image to bytes
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

# Function to convert image to HTML
def img_to_html(img_path):
    img_html = "<img src='data:image/png;base64,{}' class='img-fluid' style='max-width:100%; height:auto; width:auto;'>".format(
      img_to_bytes(img_path)
    )
    return img_html

# Sidebar to select category
st.sidebar.title("Select Category:")
all_apps_selected = st.sidebar.radio("Show apps by category:", ["All Apps"] + list(df["Category"].unique()))

if all_apps_selected == "All Apps":
    sel_df = df
else:
    sel_df = df[df["Category"] == all_apps_selected]

# background_image_url = "https://i.imgur.com/WvNNbrV.jpg"
background_image_url = "https://buntingfamilypharmacy.com/wp-content/uploads/2019/01/50-Beautiful-and-Minimalist-Presentation-Backgrounds-031.jpg"

page_bg_img = f"""
<style>

h3 {{
    --tw-text-opacity: 1;
    color: rgb(102 102 102/var(--tw-text-opacity));
    line-height: 1.5;
    font-weight: 600;
    font-size: 1.125rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;    
    flex: 1 1 0%;
    margin: 0;
    
}}

[data-testid="stAppViewContainer"] > .main {{
background-image: url('{background_image_url}');
background-size: 180%;
background-position: top left;
background-repeat: repeat;
background-attachment: local;
}}
.scaling-box {{
    background-color: #F9F9F9;
    border: 1px solid #ddd;
    padding: 10px;
    margin: 10px;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    transition: 0.3s;
    border-radius: 5px 5px 5px 5px;
    text-align: center;
    height: auto;
    display: flex;
    flex-direction: column;
    justify-content: space-between
}}
.scaling-box:hover {{
    transform: scale(1.1);
}}
.scaling-box-description {{
    margin-top: auto;
}}
.css-1dgmtll {{
    display: none
}}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

# Show apps in 3 columns
st.title("🌏 BTG Web Application Gallery")


num_cols = 3
applist = st.container()
for i in range(0, len(sel_df), num_cols):
    row = applist.columns(num_cols)
    for j in range(num_cols):
        if i + j < len(sel_df):
            app = sel_df.iloc[i + j]
            app_name = app["App"].replace(" ", "_")
            screenshot_path = generate_screenshot(app["URL"], app_name)
            with row[j]:
                st.markdown(f'''
                    <div class="scaling-box">
                        <h3>{app["App"]}</h3>
                        <div class="scaling-box-inner">
                            <a href="{app["URL"]}">{img_to_html(screenshot_path)}</a>
                        </div>
                        <p class="scaling-box-description">{app["Description"]}</p>
                    </div>
                ''', unsafe_allow_html=True)


def app1():
    # Replace with the path to your Python executable and the path to your script
    subprocess.run(["python", "apps/pdfmerger/merge.py"])



with st.sidebar:
    if st.button("Logout"):
        utils.logout()
        st.experimental_rerun()