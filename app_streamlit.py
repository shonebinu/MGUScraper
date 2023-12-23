import streamlit as st
from scraper import scrape

def main():
    st.set_page_config(page_title="MGU Scraper")
    st.title("MGU Scraper")

    start_prn = st.number_input("Enter Start PRN:", min_value=0, value=None, key='start_prn')
    end_prn = st.number_input("Enter End PRN:", min_value=0, value=None, key='end_prn')
    exam_id = st.number_input("Enter Exam ID:", min_value=0, value=None, key='exam_id')

    csv_string = ''

    # Check if inputs have changed
    inputs_changed = st.session_state.start_prn != start_prn or st.session_state.end_prn != end_prn or st.session_state.exam_id != exam_id

    # Display "Run Scraping" button only if inputs changed or scraping is completed
    if inputs_changed or st.button("Run Scraping"):
        with st.spinner("Scraping in progress..."):
            data = scrape(exam_id, start_prn, end_prn)
            csv_string = '\n'.join([','.join(map(str, row)) for row in data])

        st.success("Scraping complete!")

    # Display download button below the "Run Scraping" button
    if csv_string:
        filename = f'MGU_Scraper_Output_{exam_id}_{start_prn}_{end_prn}.csv'
        st.download_button(label='Download CSV', data=csv_string, mime='text/csv', key='download_button', help="Click to download the CSV file", file_name=filename)

if __name__ == "__main__":
    main()
