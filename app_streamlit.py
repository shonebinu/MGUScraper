import streamlit as st
from scraper import scrape_and_write_to_csv

def main():
    st.set_page_config(page_title="MGU Scraper")
    st.title("MGU Scraper")

    start_prn = st.number_input("Enter Start PRN:", min_value=0)
    end_prn = st.number_input("Enter End PRN:", min_value=0)
    exam_id = st.number_input("Enter Exam ID:", min_value=0)

    csv_string = ''

    if st.button("Run Scraping"):
        data = scrape_and_write_to_csv(exam_id, start_prn, end_prn)
        csv_string = '\n'.join([','.join(map(str, row)) for row in data])
        
    st.download_button('Download CSV', csv_string, 'text/csv')

if __name__ == "__main__":
    main()
