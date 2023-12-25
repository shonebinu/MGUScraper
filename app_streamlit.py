import streamlit as st
import pandas as pd
from scraping.exam_result_processor import scrape_results
from scraping.exam_data_fetcher import get_exam_names_and_ids

def main():
    """
    Streamlit app for MGU Scraper.
    """
    st.set_page_config(page_title="MGU Scraper")
    st.title("MGU Scraper")

    url = "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/"

    exams = get_exam_names_and_ids(url)

    start_prn = st.number_input("Enter Start PRN:", min_value=0, value=None, key='start_prn')
    end_prn = st.number_input("Enter End PRN:", min_value=0, value=None, key='end_prn')

    selected_exam = st.selectbox("Select an exam", ["Select an option"] + list(exams.keys()))

    data = None
    exam_id = None

    if st.button("Run Scraping"):
        if (selected_exam == 'Select an option'):
            st.warning('Select an exam')
            return
        if (start_prn is None or end_prn is None):
            st.warning("Enter valid numeric PRN's")
            return
        with st.spinner("Scraping in progress..."):
            exam_id = exams[selected_exam]
            data = scrape_results(url, exam_id, start_prn, end_prn)

            if data is None:
                st.error("Error: Failed to retrieve data. Please check your inputs.")
                return

            if len(data) <= 1:
                st.error("Error: No data found. Check the entered register numbers or exam.")
                return

        st.success("Scraping complete!")

    # Display download button below the "Run Scraping" button
    if data:
        filename = f'MGU_Scraper_Output_{exam_id}_{start_prn}_{end_prn}.csv'
        st.download_button(
            label='Download CSV',
            data='\n'.join([','.join(map(str, row)) for row in data]),
            mime='text/csv',
            key='download_button',
            help="Click to download the CSV file",
            file_name=filename
        )

        df = pd.DataFrame(data[1:], columns=data[0])
        st.dataframe(df, hide_index=True)

if __name__ == "__main__":
    main()
