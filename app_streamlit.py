import streamlit as st
import tempfile
import os
from scraper import scrape_and_write_to_csv

def main():
    st.set_page_config(page_title="MGU Scraper")
    st.title("MGU Scraper")

    start_prn = st.number_input("Enter Start PRN:", min_value=0)
    end_prn = st.number_input("Enter End PRN:", min_value=0)
    exam_id = st.number_input("Enter Exam ID:", min_value=0)

    if st.button("Run Scraping"):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            csv_file_path = temp_file.name
            scrape_and_write_to_csv(exam_id, start_prn, end_prn, csv_file_path)
        
        # Provide a download link
        st.markdown(f"[Download Output File](sandbox:/mnt/data/{os.path.basename(csv_file_path)})")

if __name__ == "__main__":
    main()
