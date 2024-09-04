import streamlit as st
from cryptography.fernet import Fernet

def encrypt_file_function():
    st.header("File Encryption")
    uploaded_file = st.file_uploader("Choose a file to encrypt")

    if uploaded_file is not None:
        # Simulate encryption process
        key = Fernet.generate_key()
        cipher = Fernet(key)

        file_content = uploaded_file.read()
        encrypted_content = cipher.encrypt(file_content)

        st.write("File encrypted successfully!")
        st.download_button(label="Download Encrypted File", data=encrypted_content, file_name="encrypted_file.enc")
