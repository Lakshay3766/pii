import pikepdf
from io import BytesIO
import streamlit as st

def pdf_protection_function():
    st.header("PDF Password Protection")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        password = st.text_input("Enter a password to protect the PDF", type="password")
        if password:
            try:
                pdf = pikepdf.Pdf.open(uploaded_file)
                pdf_output = BytesIO()
                pdf.save(pdf_output, encryption=pikepdf.Encryption(owner=password, user=password))
                pdf_output.seek(0)
                st.download_button(
                    label="Download Protected PDF",
                    data=pdf_output,
                    file_name="protected_pdf.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
