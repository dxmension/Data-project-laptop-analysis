from typing import Dict, Optional
import streamlit as st
from groq import Groq
from PIL import Image
import pandas as pd
import plotly.express as px


st.set_page_config(layout="centered")

with open("styles.css", "r") as file:
    st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)

CLIENT = Groq(api_key="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")


def assess_laptop(config: Dict[str, str]) -> Dict[str, float]:

    scoring_info = {}
    

    prompt = f'''
        Rate the following laptop configuration on a scale of 0-10 in terms of gaming, software development, video editing, general use, graphic design, data science:

        - Brand: {config['Name']}
        - Screen Size: {config['Display Size']} 
        - Screen Resolution: {config['Resolution']}
        - CPU: {config["CPU"]}
        - GPU: {config['GPU']}
        - Memory: {config['SSD/HDD Capacity']} 
        - RAM Capacity: {config['RAM']} 

        Please provide only key-value pair, example: "Gaming - 9, Video editing - 5, etc."
    '''


    chat_completion = CLIENT.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
    
    response = chat_completion.choices[0].message.content
    response = response.split('\n')[1:]

    for idx, item in enumerate(response, start=1):
        if item:
            key, val = item.split(" - ")
            scoring_info[key[2:]] = [float(val)]

    return scoring_info
    
def load_laptop(config: Dict[str, str]) -> Dict[str, str]:
    
    df = pd.read_csv("data/laptops_data.csv")


    laptop = df[df["gpu_brand"] == config["GPU"].split()[0]].sample(n=1)
    laptop["Name"] = df["brand"] + " " +  df["model"]
    laptop["CPU"] = df["cpu_brand"] + " " + df["cpu_model"]
    laptop["SSD/HDD Capacity"] = df["hdd_capacity"] + df["ssd_capacity"]

    laptop.rename(columns={"gpu": "GPU",
                        "display_diagonal": "Display Size",
                        "resolution": "Resolution",
                        "ram": "RAM"}, inplace=True)
    
    laptop["Display Size"] = laptop["Display Size"].astype('object')
    laptop["RAM"] = laptop["RAM"].astype('object')
    laptop["SSD/HDD Capacity"] = laptop["SSD/HDD Capacity"].astype('object')

    laptop = laptop[["Name", "GPU", "CPU", "Display Size", "Resolution", "RAM", "SSD/HDD Capacity"]]

    laptop_config = laptop.to_dict('records')[0]

    return laptop_config
    

def get_laptop_config(user_prompt: str) -> Dict[str, str]:
    
    prompt = f'''provide me only key value pair of name, 
                configuration that includes only GPU, CPU, 
                Display size, resolution, RAM, SSD/HDD capacity,
                price of a laptop based on following user preferences (provide only one laptop option):\n{user_prompt}\n\n
                Output must be provided as following sample:\n
                Name: Acer Aspire 3\n
                GPU: Intel Iris Xe Graphics\n
                CPU: 11th Gen Intel Core i3-1115G4\n
                Display Size: 15.6 inches\n
                Resolution: Full HD (1920 x 1080)\n
                RAM: 8GB LPDDR4\n
                SSD/HDD Capacity: 512GB SSD\n
                Price: $849\n\n
                This laptop offers good performance for general use, including web browsing, email, office work, and streaming. The Intel Iris Xe Graphics provide adequate graphics power, while the 11th Gen Core i3 processor offers faster processing speeds. The 15.6-inch Full HD display is ideal for watching movies and working on documents. The 8GB RAM and 512GB SSD provide ample storage and fast loading times.'''
    
    chat_completion = CLIENT.chat.completions.create(messages=[
        {"role": "user", "content": prompt}],
        model="llama3-8b-8192"
    )
    response = chat_completion.choices[0].message.content
    response = response.split("\n")
    laptop_cfg = {}
    for elem in response[1:]:
        if ":" in elem:
            feature = elem.split(": ")
            try:
                laptop_cfg[feature[0]] = feature[1]
            except IndexError:
                st.markdown('''
                            <style>
                                .error-msg {
                                    text-align: center;
                                }
                            </style>
                            ''', unsafe_allow_html=True)
                st.markdown("<h4 class='error-msg'>Laptop has been lost while searching, try one more time ;(</h4>", unsafe_allow_html=True)
                return None


    return laptop_cfg

def get_prompt() -> Optional[str]:
    st.markdown("""
        <style>
            .text {
                text-align:center    
            }
            .highlight {
                color: transparent;
                -webkit-text-stroke: 1px #405cf5;
                text-shadow: 0 0 5px #405cf5; /* Adjust the glow color and spread */
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"<h1 class='text'>Enter Your <span class='highlight'>Laptop Preferences</span> for <br> Personalized Recommendation</h1>",
                unsafe_allow_html=True)
    preferences = st.text_input("Provide Preferences", label_visibility="hidden")

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        show_btn = st.button("Show Laptop")
        if show_btn:
            return preferences
        
    return None

def show_laptop_info(config: Dict[str, str]) -> None:
    laptop_name = config["Name"]
    with st.container(height=550, border=True):
        st.header(laptop_name)
        for key, val in config.items():
            if key not in ["Name", "Price"]:
                st.markdown(f"<span style='font-weight: bold; font-size: 16px'>{key}</span><br>{val}", unsafe_allow_html=True)

def show_laptop_card(config: Dict[str, str]) -> None:
    laptop_name = config["Name"]
    laptop_price = config["Price"]
    with st.container(height=550, border=True):
        laptop_image = Image.open("pages/1.jpg")
        st.image(laptop_image)

        st.markdown(f"<h3>{laptop_name}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='opacity: 0.5; margin-bottom: 1px'>Available in KZ</p>", unsafe_allow_html=True)
        st.markdown(f"<h5 style='font-weight: 600'>{laptop_price}.99</h3>", unsafe_allow_html=True)

        btn1, btn2 = st.columns([1, 1])
        with btn1:
            track = st.button("Official Website", type="primary")
        with btn2:    
            website = st.button("Kaspi.kz Page", type="secondary")

def show_charts(config: Dict[str, str]) -> None:
    with st.container(height=600, border=True):
        similar_laptop_cfg = load_laptop(config)

 
        cfg_scoring = assess_laptop(config=config)
        cfg_scoring_1 = assess_laptop(config=similar_laptop_cfg)

        df1 = pd.DataFrame(cfg_scoring)
        df1 = df1.transpose().reset_index()
        df1.columns = ["Category", "Value"]
        df1 = df1.sort_values(by="Value")

        df2 = pd.DataFrame(cfg_scoring_1)
        df2 = df2.transpose().reset_index()
        df2.columns = ["Category", "Value"]
        df2 = df2.sort_values(by="Value")

        fig = px.bar(df1, y="Category", x="Value", color="Category")

        fig.update_layout(showlegend=False)
        fig.update_yaxes(title="")
        fig.update_xaxes(title="")

        st.header(f"General Assessment of {config["Name"]}")
        st.plotly_chart(fig)
        

def execute_recomendation():
    prompt = get_prompt()
    
    if prompt:
        suggested_laptop_cfg: Dict[str, str] = get_laptop_config(prompt)
        card_column, gap, description_column = st.columns([1, 0.2, 1])  

        with card_column:
            show_laptop_card(suggested_laptop_cfg)
        with description_column:
            show_laptop_info(suggested_laptop_cfg)

        show_charts(suggested_laptop_cfg)

def main():
    execute_recomendation()


if __name__ == "__main__":
    main()