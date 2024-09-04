import re
import streamlit as st

def redact_text_function():
    st.header("Text Redaction")
    input_text = st.text_area("Enter text for redaction")

    # Example: Redact emails and phone numbers
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    phone_pattern = r'\b[6-9]\d{9}\b'

    if input_text:
        redacted_text = re.sub(email_pattern, '[REDACTED EMAIL]', input_text)
        redacted_text = re.sub(phone_pattern, '[REDACTED PHONE]', redacted_text)
        st.text_area("Redacted Text", value=redacted_text)
