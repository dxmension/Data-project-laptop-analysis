from typing import Dict, Union, List, Tuple
import streamlit as st
import pandas as pd
import numpy as np
from groq import Groq
import plotly.graph_objects as go
import os

def load_average_laptop() -> Dict[str, Dict[str, Union[str, float]]]:
    """
    Load 3 random laptops from laptops_data.csv by usage type (gaming, non-gaming, apple)
    and save their configurations into dictionary.

    Args:
        None

    Returns:
        laptop_list(Dict[str, Dict[str, Union[str, float]]]): Dictonary contaning 3 laptop configurations.
    """
    laptop_list = {}
    data = load_data()
    data.rename(columns={"brand": "brand_name",
                            "display_diagonal": "screen_size",
                            "resolution": "screen_resolution",
                            "gpu": "gpu_model",
                            "ram": "ram_capacity"}, inplace=True)

    gaming_laptop = data[data["gpu_model"].str.contains("RTX")].sample(n=1).copy()
    mac = data[data["brand_name"] == "Apple"].sample(n=1).copy()
    laptop = data[~data["gpu_model"].str.contains("RTX")].sample(n=1).copy()

    # Add 'memory' column
    gaming_laptop["memory"] = gaming_laptop["hdd_capacity"] + gaming_laptop["ssd_capacity"]
    mac["memory"] = mac["hdd_capacity"] + mac["ssd_capacity"]
    laptop["memory"] = laptop["hdd_capacity"] + laptop["ssd_capacity"]

    gaming_laptop_dict = gaming_laptop.to_dict('records')[0]
    mac_dict = mac.to_dict('records')[0]
    laptop_dict = laptop.to_dict('records')[0]

    laptop_list = {
        "gaming laptop": gaming_laptop_dict,
        "macbook": mac_dict,
        "laptop": laptop_dict
    }

    return laptop_list

def load_data() -> pd.DataFrame:
    """
    Load laptops database from local directory.

    Args:
        None

    Returns:
        data (pd.DataFrame): Dataframe with laptop configurations
    """
    data = pd.read_csv("data/laptops_data.csv")
    return data

def assess_laptop(config: Dict[str, Dict[str, Union[str, float]]]) -> Dict[str, float]:
    """
    Assess laptop by provided config according to five criteras: 
        genral use, gaming, data science, graphic design, and video editing on a scale of 1-10.

    Grading process is handled by GroqCloud API (Llama3).

    Args:
        config(Dict[str, Dict[str, Union[str, float]]]): Laptop configuration to assess.

    Returns:
        scoring_info (Dict[str, float]): Dictionary containing grading results.
    """
    scoring_info = {}
    client = Groq(
        api_key=os.environ["GROQ_API_KEY"])
    

    prompt = f'''
        Rate the following laptop configuration on a scale of 0-10 in terms of gaming, software development, video editing, general use, graphic design, data science:

        - Brand: {config['brand_name']}
        - Screen Size: {config['screen_size']} inches
        - Screen Resolution: {config['screen_resolution']}
        - CPU Brand: {config['cpu_brand']}
        - CPU Model: {config['cpu_model']}
        - CPU Frequency: {config['cpu_frequency']} GHz
        - GPU Brand: {config['gpu_brand']}
        - GPU Model: {config['gpu_model']}
        - Memory Type: {config['memory_type']}
        - Memory: {config['memory']} GB
        - RAM Capacity: {config['ram_capacity']} GB

        Please provide only key-value pair, example: "Gaming - 9, Video editing - 5, etc."
    '''


    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
    
    response = chat_completion.choices[0].message.content
    response = response.split('\n')[1:]

    for idx, item in enumerate(response, start=1):
        if item:
            key, val = item.split(" - ")
            scoring_info[key[2:]] = float(val)

    return scoring_info

def show_sidebar(data: pd.DataFrame) -> Dict[str, Dict[str, Union[str, float]]]:
    """
    Implements sidebar menu logic to receive laptop configuration provided by user input.

    Args:
        data (pd.DataFrame): Dataframe with laptop configurations.

    Returns:
        laptop_cfg (Dict[str, Dict[str, Union[str, float]]]): Dictionary containing user configuration settings.
    """
    laptop_cfg = {}

    st.sidebar.title("Laptop Configuration")
    st.sidebar.write("Provide all necessary information about your laptop")

    # General Infomation about the laptop
    st.sidebar.header("General Information")
    laptop_cfg["brand_name"] = st.sidebar.selectbox("Brand Name", 
                                    data["brand"].unique())
    laptop_cfg["screen_size"] = st.sidebar.number_input("Screen Size, in", 
                                        min_value=min(data["display_diagonal"].unique()),
                                        max_value=max(data["display_diagonal"].unique()),
                                        step=0.1)
    laptop_cfg["screen_resolution"] = st.sidebar.selectbox("Screen Resolution",
                                            data["resolution"].unique())
    
    # CPU Information of the laptop
    st.sidebar.header("CPU Information")
    cpu_mappings = {
        "AMD": data[data["cpu_brand"] == "AMD"]["cpu_model"].unique(),
        "Intel": data[data["cpu_brand"] == "Intel"]["cpu_model"].unique(),
        "Apple": data[data["cpu_brand"] == "Apple"]["cpu_model"].unique(),
    }
    if laptop_cfg["brand_name"] != "Apple":
        laptop_cfg["cpu_brand"] = st.sidebar.selectbox("CPU Brand",
                                        data[data["cpu_brand"] != "Apple"]["cpu_brand"].unique())
        laptop_cfg["cpu_model"] = st.sidebar.selectbox("CPU Model",
                                        cpu_mappings[laptop_cfg["cpu_brand"]])
        laptop_cfg["cpu_frequency"] = st.sidebar.number_input("CPU Frequency, GHz",
                                                min_value=min(data["cpu_frequency"].unique()),
                                                max_value=max(data["cpu_frequency"].unique()),
                                                step=0.1)
    else:
        laptop_cfg["cpu_brand"] = "Apple"
        laptop_cfg["cpu_model"] = st.sidebar.selectbox("CPU Model",
                                        cpu_mappings[laptop_cfg["cpu_brand"]])
        laptop_cfg["cpu_frequency"] = st.sidebar.number_input("CPU Frequency, GHz",
                                                min_value=min(data["cpu_frequency"].unique()),
                                                max_value=max(data["cpu_frequency"].unique()),
                                                step=0.1)
        
    # GPU Configuration
    st.sidebar.header("GPU Information")
    graphic_type = st.sidebar.radio("Graphics Type", ["Integrated", "Dedicated", "Both"])
    if graphic_type != "Integrated":    
        laptop_cfg["gpu_brand"] = st.sidebar.selectbox("GPU Brand",
                                        ["NVIDIA", "AMD"])
        model_placeholders = {
            "AMD": "Radeon RX 570",
            "NVIDIA": "GeForce RTX 2060 Ti"
        }
        laptop_cfg["gpu_model"] = st.sidebar.text_input("GPU Model", placeholder=model_placeholders[laptop_cfg["gpu_brand"]])
    else:
        laptop_cfg["gpu_brand"] = f"Integrated {laptop_cfg["cpu_brand"]}"
        laptop_cfg["gpu_model"] = f"{laptop_cfg["cpu_brand"]}"

    # Memory Configuration
    st.sidebar.header("Memory Information")
    laptop_cfg["memory_type"] = st.sidebar.radio("Memory Type",
                                data["memory_type"].unique())
    if laptop_cfg["memory_type"] == "SHDD":
        laptop_cfg["hdd"] = st.sidebar.selectbox("HDD Capacity, GB", [256, 512, 1024, 2048, 3096, 4096, 5128])
        
        laptop_cfg["ssd"] = st.sidebar.selectbox("SSD Capacity, GB", [256, 512, 1024, 2048, 3096, 4096, 5128])
    else:
        laptop_cfg["memory"] = st.sidebar.selectbox('Memory Capacity, GB', [256, 512, 1024, 2048, 3096, 4096, 5128])

    # RAM Configuration
    st.sidebar.header("RAM Information")
    laptop_cfg["ram_capacity"] = st.sidebar.number_input("RAM Capacity, GB",
                                        min_value=0,
                                        max_value=max(data["ram"].unique()),
                                        step=8)

    return laptop_cfg

def show_main(data: pd.DataFrame) -> None:
    """
    LShows main page of the application including sidebar navigation.

    Args:
        data (pd.DataFrame): Dataframe with laptop configurations.

    Returns:
        None
    """
    st.title("💻 Laptopio - your laptop assessor")
    st.subheader("""Laptopio offers a platform designed to help you find the perfect laptop tailored to your needs.""")
    st.write('''Whether you're a gamer, a professional, or a casual user, our app leverages advanced data analytics
                to compare laptops against the average market offerings and recommend the best options based on 
                your preferences.''')
    

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        toggle_configurator = st.button("Assess Laptop", type="primary")
    with col2:
        toggle_recommendations_detailed = st.button("Recommend Laptop (detailed)", type="secondary")
    with col3:
        toggle_recommendations_simplified = st.button("Recommend Laptop (simplified)", type="secondary")

    laptop_configuration = show_sidebar(data)
    configurations = load_average_laptop()
    
    if laptop_configuration["brand_name"] == "Apple":
        comparison_configuration = configurations["macbook"]
    elif "RTX" in laptop_configuration["gpu_model"] or "GTX" in laptop_configuration["gpu_model"]:
        comparison_configuration = configurations["gaming laptop"]
    else:
        comparison_configuration = configurations["laptop"]

    if toggle_configurator:

        laptop_assessment = assess_laptop(laptop_configuration)
        comparison_assessment = assess_laptop(comparison_configuration)

        data1 = {"Feature": list(laptop_assessment.keys()), "Rating1": list(laptop_assessment.values())}
        data2 = {"Feature": list(comparison_assessment.keys()), "Rating2": list(comparison_assessment.values())}

        df1 = pd.DataFrame(data1)
        df2 = pd.DataFrame(data2)

        df = df1.merge(df2)

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=df["Rating1"],
            theta=df["Feature"],
            fill="toself",
            name="Your Laptop"
        ))
        fig.add_trace(go.Scatterpolar(
            r=df["Rating2"],
            theta=df["Feature"],
            fill="toself",
            name=f"{comparison_configuration['brand_name']} {comparison_configuration['model']}"
        ))

        fig.update_layout(
            width=1000,
            height=500,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )
            ),
            showlegend=True
        )

        st.title("Laptop Assessment Chart")
        st.plotly_chart(fig)
        st.markdown(f"<hr></hr>", unsafe_allow_html=True)
        st.write("Assessment criterias are subjective viewpoint of the app creator as well as assessment points provided using Generative AI APIs, my goal is to show general view from the perspective of machine, not professional with high expertise.")


def run() -> None:
    st.set_page_config(page_title="Laptopio",
                        page_icon=":computer:",
                        layout="centered")
    
    with open("styles.css") as file:
        st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)
    
    data = load_data()
    show_main(data)


def main():
    run()

if __name__ == "__main__":
    main()