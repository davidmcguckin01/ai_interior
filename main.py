import os
import replicate
import streamlit as st
from tinydb import TinyDB
from dotenv import load_dotenv
import json

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """

st.markdown(hide_menu_style, unsafe_allow_html=True)


def configure():
    load_dotenv()

configure()

db = TinyDB("data.json")

"""
# Welcome to AI Interior

#
Input your prompt and we will generate a design for you.
_Process may take up to 30 seconds_
"""

instruction = "Realistic architectural rendering of " + st.text_input("Enter your prompt") + ", highly detailed realistic modern Home with a view, Photorealistic, rendered in unreal engine, ultradetail"

if st.button('Generate'):
    model = replicate.models.get("stability-ai/stable-diffusion")
    image = model.predict(prompt=instruction)
    st.image(image, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
    if instruction:
        db.insert({
            "instruction" : instruction, 
            "image" : image
        })

st.markdown('#')
st.markdown('#')
st.markdown('#') 

tab1, tab2, tab3 = st.tabs(["Gallery", "Write great prompts", "Prompt Examples"])
with tab1:
    with open('data.json') as json_file:
        data = json.load(json_file)

    count = 0

    for i in data['_default']:
        count += 1

    gallery1 = data['_default'][str(count-1)]['image']
    gallery2 = data['_default'][str(count-2)]['image']
    gallery3 = data['_default'][str(count-3)]['image']
    st.image(gallery1, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
    st.image(gallery2, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
    st.image(gallery3, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
    
with tab2:
    """
    #### How to write great prompts
    - Be As Specific as You Can 
    - Name Specific Art Styles or Mediums -> “acrylic painting”
    - Name Specific Artists ie. “by (Artist Name)” 
    - Weight Your Keywords ie. “cute, grey cat” -> “[cute],((grey cat)).”
    - Tweak Other Important Settings such as CFG, Sampling Method and Sampling Steps

    #### Cool words to use in your prompt
    - 50mm
    - 35mm
    - cinematic lighting
    - award winning photo,
    - ultrarealistic
    - unreal engine
    - rendered in vray

    #### Words to influence your architectural design
    - 
    """

with tab3:
    """
    ## _Coming soon_
    """