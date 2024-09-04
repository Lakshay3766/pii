import streamlit as st

def calculate_risk_score_function():
    st.header("Risk Score Calculator")
    data = st.slider("Select risk parameters (1 - 100)", 1, 100, 50)

    # Simple risk calculation logic
    risk_score = data * 2  # Just an example of calculating risk score

    st.write(f"Your risk score is: {risk_score}")
