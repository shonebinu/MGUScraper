import streamlit as st
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

    selected_exam = st.selectbox("Select an exam", list(exams.keys()))
    exam_id = int(exams[selected_exam])

    csv_string = ''

    if st.button("Run Scraping"):
        with st.spinner("Scraping in progress..."):
            data = scrape_results(url, exam_id, start_prn, end_prn)

            if data is None:
                st.error("Error: Failed to retrieve data. Please check your inputs.")
                return

            csv_string = '\n'.join([','.join(map(str, row)) for row in data])

            if len(data) <= 1:
                st.error("Error: No data found. Check the entered register numbers or exam.")
                return

        st.success("Scraping complete!")

    # Display download button below the "Run Scraping" button
    if csv_string:
        filename = f'MGU_Scraper_Output_{exam_id}_{start_prn}_{end_prn}.csv'
        st.download_button(
            label='Download CSV',
            data=csv_string,
            mime='text/csv',
            key='download_button',
            help="Click to download the CSV file",
            file_name=filename
        )

if __name__ == "__main__":
    main()
