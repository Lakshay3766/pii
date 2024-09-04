import streamlit as st
import os
import time

def monitor_function():
    st.header("Watchdog Monitor")
    directory = st.text_input("Enter the directory to monitor")

    if directory:
        st.write(f"Monitoring {directory} for changes...")
        files_initial = set(os.listdir(directory))

        while True:
            time.sleep(5)  # Simulate a delay
            files_now = set(os.listdir(directory))
            added = files_now - files_initial
            removed = files_initial - files_now

            if added:
                st.write(f"New files: {', '.join(added)}")
            if removed:
                st.write(f"Removed files: {', '.join(removed)}")
            files_initial = files_now
