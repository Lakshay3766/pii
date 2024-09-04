import streamlit as st
from io import BytesIO
from PIL import Image

def file_converter_function():
    st.header("File Converter")
    uploaded_file = st.file_uploader("Choose a file to convert", type=["png", "jpg", "jpeg", "pdf"])

    if uploaded_file is not None:
        if uploaded_file.type in ["image/png", "image/jpeg"]:
            image = Image.open(uploaded_file)
            buffer = BytesIO()
            image.save(buffer, format="PDF")
            st.download_button(label="Download as PDF", data=buffer.getvalue(), file_name="converted_file.pdf")
        else:
            st.warning("Currently only image to PDF conversion is supported.")
