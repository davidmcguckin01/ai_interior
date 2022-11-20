import os
import replicate
import streamlit as st
from tinydb import TinyDB
from dotenv import load_dotenv
import json
import boto3
from botocore.client import Config
import datetime
import random
from create_presigned_url import create_presigned_url
import base64
from PIL import Image
from compress_img import compress_img
import io

load_dotenv()

# Config 
s3 = boto3.client("s3") # s3 client
db = TinyDB("data.json") # database for gallery

# Hide streamlit default menu
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """

st.markdown(hide_menu_style, unsafe_allow_html=True)

# Welcome message
"""
# Welcome to AI Interior

#
Input your prompt and we will generate a design for you.
_Process may take up to 30 seconds_
"""

# Prompt input
instruction = "Highly contrasting, fine detailed, photorealistic interior design rendering of " + st.text_input("Enter your prompt") + ", rendered in unreal engine, ultradetail, 50mm, cinematic lighting, Award winning photo, Ultrarealistic, Unreal engine, Rendered in vray"

# Image upload
img_upload = st.file_uploader(label = "Choose a file (Maximum size is 1024x768 or 768x1024 pixels)", accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")


file_name = str(datetime.datetime.now()) + str(random.randint(0,100))
file_name = file_name.replace(' ', '')
file_name = file_name.replace('-', '')
file_name = file_name.replace(':', '')
file_name = file_name.replace('.', '')

if img_upload:
    # Image upload
    bytes_data = img_upload.getvalue()
    s3.upload_fileobj(io.BytesIO(bytes_data), "interioraiimagestorage", str(file_name))

    # Image download
    s3.download_file('interioraiimagestorage', file_name, 'images/'+file_name+'.png')
    encoded = base64.b64encode(open("images/download.png", "rb").read())

    def image_to_data_url(filename):
        ext = filename.split('.')[-1]
        prefix = f'data:image/{ext};base64,'
        with open(filename, 'rb') as f:
            img = f.read()
        return prefix + base64.b64encode(img).decode('utf-8')

    data = image_to_data_url('images/'+file_name+'.png')

# Generate button
if st.button('Generate'):
    # Model config
    model = replicate.models.get("stability-ai/stable-diffusion")

    if img_upload:
        image = model.predict(prompt=instruction, prompt_strength = 0.5, init_image = data, num_outputs = 3, num_inference_steps = 50, guidance_scale = 7.5 )
        #image = model.predict(prompt=instruction, width = 768, init_image = data, prompt_strength = 0.7, num_outputs = 1, num_inference_steps = 30, guidance_scale = 7.5)
    else:
        image = model.predict(prompt=instruction, num_outputs = 2)
    
    # Sending result image to json db
    if instruction:
        db.insert({
            "instruction" : instruction, 
            "image" : image
        })

    # Output image
    st.image(image, caption=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")

# Additional content section
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
    - Name Specific architecture ie. “by (Artist Name)” 
    - Weight Your Keywords ie. “cute, grey cat” -> “[cute],((grey cat)).”
    - Tweak Other Important Settings such as CFG, Sampling Method and Sampling Steps

    #### Prompts to use in your prompt
    - 50mm
    - 35mm
    - cinematic lighting
    - Award winning photo,
    - Ultrarealistic
    - Unreal engine
    - Rendered in vray

    #### Words to influence your interior design
    - Wooden floor 
    - Biege blue
    - Salmon pastel
    - Minimalist white
    - Sun light 
    - Volumetric light


    """

with tab3:
    """
    "High resolution photography of a minimalistic white interior living room with a wooden floor, beige blue salmon pastel, sun light, contrast, realistic artstation concept art, hyperdetail, ultradetail, cinematic 8k, architecural rendering, unreal engine 5, rtx, volumetric light, cozy atmosphere"
    """