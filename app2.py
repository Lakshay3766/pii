import re
import pytesseract
import pdfplumber
import streamlit as st
from PIL import Image
from io import BytesIO
from cryptography.fernet import Fernet
import fitz  # PyMuPDF for editing PDFs
import tempfile
import openai

# Initialize OpenAI API Key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Importing the features from the "features" folder
from features.cloud_upload import cloud_upload_function
from features.file_converter import file_converter_function
from features.file_encryption import encrypt_file_function
from features.pdf_password_protection import pdf_protection_function
from features.risk_score import calculate_risk_score_function
from features.text_redaction import redact_text_function
from features.upload_history import upload_history_function
from features.visual_feedback import visual_feedback_function
from features.watchdog_monitor import monitor_function

# Encryption setup (generate key)
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

# Regular expressions for PII detection
aadhaar_regex = r'\b[2-9]{1}[0-9]{3}[0-9]{4}[0-9]{4}\b'
pan_regex = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
email_regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
phone_regex = r'\b[6-9]\d{9}\b'
credit_card_regex = r'\b(?:\d[ -]*?){13,16}\b'
passport_regex = r'\b[A-PR-WYa-pr-wy][1-9]\d\s?\d{4}[1-9]\b'
ip_address_regex = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

# Function to extract text from an image using Tesseract OCR
def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

# Function to extract text from a PDF using pdfplumber
def extract_text_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        all_text = ""
        for page in pdf.pages:
            all_text += page.extract_text()
    return all_text

# Function to detect PII in the extracted text
def detect_pii(text):
    detected_pii = {
        'aadhaar': re.findall(aadhaar_regex, text),
        'pan': re.findall(pan_regex, text),
        'email': re.findall(email_regex, text),
        'phone': re.findall(phone_regex, text),
        'credit_card': re.findall(credit_card_regex, text),
        'passport': re.findall(passport_regex, text),
        'ip_address': re.findall(ip_address_regex, text)
    }
    return {key: value for key, value in detected_pii.items() if value}

# Function to mask PII in the text
def mask_pii(text, pii_data):
    for aadhaar in pii_data.get('aadhaar', []):
        text = text.replace(aadhaar, 'XXXX XXXX XXXX')
    for pan in pii_data.get('pan', []):
        text = text.replace(pan, 'XXXXX0000X')
    for email in pii_data.get('email', []):
        text = text.replace(email, 'xxxxx@example.com')
    for phone in pii_data.get('phone', []):
        text = text.replace(phone, 'XXXXXXXXXX')
    for credit_card in pii_data.get('credit_card', []):
        text = text.replace(credit_card, 'XXXX XXXX XXXX XXXX')
    for passport in pii_data.get('passport', []):
        text = text.replace(passport, 'XX000000')
    for ip_address in pii_data.get('ip_address', []):
        text = text.replace(ip_address, 'XXX.XXX.XXX.XXX')
    return text

# Function to create a downloadable PDF file after masking
def mask_pii_in_pdf(pdf_file, masked_text):
    # Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(pdf_file.getvalue())
        temp_pdf_path = temp_pdf.name

    # Open the original PDF using PyMuPDF (fitz)
    doc = fitz.open(temp_pdf_path)

    # For each page, replace text with the masked text by overlaying it
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_text = page.get_text("text")
        page_text_masked = mask_pii(page_text, detect_pii(page_text))
        text_to_insert = page_text_masked
        page.insert_text((50, 50), text_to_insert, fontsize=12, color=(0, 0, 0))

    # Save the new masked PDF
    output_pdf = BytesIO()
    doc.save(output_pdf)
    doc.close()
    output_pdf.seek(0)
    return output_pdf

# Function to query ChatGPT for PII suggestions
def get_pii_suggestions(pii_detected, organization):
    prompt = f"I have detected the following PII:\n\n{pii_detected}\n\nI want to submit details for {organization}. Can you suggest what PII is required to submit?"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that helps users identify which PII is needed for submission."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"Error communicating with OpenAI: {str(e)}"

# Add custom CSS for UI styling
st.markdown("""
    <style>
        body {
            background-color: #0d0d0d;
        }
        .main-container {
            background-color: #1f1f1f;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        }
        .header-title {
            text-align: center;
            color: #ffffff;
            font-size: 36px;
            font-weight: 700;
            letter-spacing: 2px;
            padding: 20px;
        }
        .extracted-text, .detected-pii, .masked-text {
            background-color: #292929;
            color: #ffffff;
            padding: 10px;
            margin-top: 20px;
            border-radius: 8px;
            font-size: 18px;
            font-family: 'Courier New', Courier, monospace;
        }
        .subheader {
            color: #00ff99;
            font-size: 24px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .stButton button {
            background-color: #007bff;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            transition: background-color 0.3s ease;
        }
        .stButton button:hover {
            background-color: #0056b3;
        }
        .detected-pii-box {
            background-color: #2b2b2b;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.2);
            color: #00ff99;
            font-size: 16px;
        }
        .icon {
            color: #00ff99;
            margin-right: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar content with a collapsible section for features
with st.sidebar.expander("Features"):
    feature = st.radio(
        "Choose a feature:",
        (
            "PII Detection",
            "Cloud Upload",
            "File Converter",
            "File Encryption",
            "PDF Password Protection",
            "Risk Score Calculation",
            "Text Redaction",
            "Upload History",
            "Visual Feedback",
            "Watchdog Monitor"
        )
    )

# Adding a custom header and description for the app
st.markdown("<h1 class='header-title'>PII Detector Application</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#dcdcdc;font-size:18px;'>Welcome to the PII Detector and Utility Tools app. Choose a feature from the left menu to start.</p>", unsafe_allow_html=True)

# Input organization and purpose to get PII suggestions from ChatGPT
organization = st.text_input("Enter the organization name (e.g., Spotify Premium ID submission):")

# Main feature logic based on selection
if feature == "PII Detection":
    st.markdown(f"<h1 class='header-title'><i class='icon fas fa-user-secret'></i>PII Detector</h1>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload a PDF or Image file for PII detection", type=["pdf", "png", "jpg", "jpeg"])
    if uploaded_file:
        file_type = uploaded_file.type
        if file_type == "application/pdf":
            extracted_text = extract_text_from_pdf(uploaded_file)
            detected_pii = detect_pii(extracted_text)
            st.markdown("<div class='extracted-text'><span class='subheader'>Extracted Text:</span>", unsafe_allow_html=True)
            st.text(extracted_text)
            st.markdown("</div>", unsafe_allow_html=True)
            if detected_pii:
                st.markdown("<div class='detected-pii-box'><span class='subheader'>Detected PII:</span>", unsafe_allow_html=True)
                st.json(detected_pii)
                st.markdown("</div>", unsafe_allow_html=True)

                if organization and st.button("Get PII Submission Suggestions"):
                    suggestions = get_pii_suggestions(detected_pii, organization)
                    st.markdown(f"**Suggestions for {organization}:**\n\n{suggestions}")

            elif not detected_pii:
                st.markdown("<div class='extracted-text'><span class='subheader'>No PII Detected:</span> You can safely upload this document.</div>", unsafe_allow_html=True)

            if any(detected_pii.values()):
                if st.button("Mask PII"):
                    masked_pdf = mask_pii_in_pdf(uploaded_file, extracted_text)
                    st.download_button(label="Download Masked PDF", data=masked_pdf, file_name="masked_document.pdf")
        else:
            image = Image.open(uploaded_file)
            extracted_text = extract_text_from_image(image)
            detected_pii = detect_pii(extracted_text)
            st.markdown("<div class='extracted-text'><span class='subheader'>Extracted Text:</span>", unsafe_allow_html=True)
            st.text(extracted_text)
            st.markdown("</div>", unsafe_allow_html=True)
            if detected_pii:
                st.markdown("<div class='detected-pii-box'><span class='subheader'>Detected PII:</span>", unsafe_allow_html=True)
                st.json(detected_pii)
                st.markdown("</div>", unsafe_allow_html=True)

                if organization and st.button("Get PII Submission Suggestions"):
                    suggestions = get_pii_suggestions(detected_pii, organization)
                    st.markdown(f"**Suggestions for {organization}:**\n\n{suggestions}")

            elif not detected_pii:
                st.markdown("<div class='extracted-text'><span class='subheader'>No PII Detected:</span> You can safely upload this document.</div>", unsafe_allow_html=True)

elif feature == "Cloud Upload":
    cloud_upload_function()

elif feature == "File Converter":
    file_converter_function()

elif feature == "File Encryption":
    encrypt_file_function()

elif feature == "PDF Password Protection":
    pdf_protection_function()

elif feature == "Risk Score Calculation":
    calculate_risk_score_function()

elif feature == "Text Redaction":
    redact_text_function()

elif feature == "Upload History":
    upload_history_function()

elif feature == "Visual Feedback":
    visual_feedback_function()

elif feature == "Watchdog Monitor":
    monitor_function()
