import streamlit as st

uploaded_files = []

def upload_history_function():
    st.header("Upload History")
    uploaded_file = st.file_uploader("Choose a file to upload")

    if uploaded_file is not None:
        uploaded_files.append(uploaded_file.name)
        st.success(f"{uploaded_file.name} uploaded successfully!")

    st.subheader("History of Uploaded Files")
    for file in uploaded_files:
        st.write(file)
