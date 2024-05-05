import streamlit as st
import pandas as pd
from scraping.exam_result_processor import scrape_results, scrape_results_pg
from scraping.exam_data_fetcher import get_exam_names_and_ids


def main():
    """
    Streamlit app for MGU Scraper.
    """
    st.set_page_config(page_title="MGU Scraper", page_icon="./assets/favicon.ico")
    st.title("MGU Scraper")

    # Add a note about data ownership and permission
    st.info(
        "Note: The data provided by this app belongs to the respective university. Please ensure you have permission from the data owner before using this tool."
    )

    selected_category = st.radio("Select Category", ["UG", "PG"])
    if selected_category:
        semester_array = get_exam_names_and_ids(selected_category)

        # Create a list of semester names
        semesters = ["Select a semester"] + [
            f"Semester {i+1}" for i in range(len(semester_array))
        ]

        # Allow the user to select a semester
        selected_semester = st.selectbox("Select a semester", semesters)

        # If a semester is selected, provide a list of exams for that semester
        if selected_semester != "Select a semester":
            selected_semester_index = (
                semesters.index(selected_semester) - 1
            )  # Subtract 1 to get the index in semester_array
            selected_semester_data = semester_array[selected_semester_index]

            # Extract exam names from the selected semester's data
            exam_names = list(selected_semester_data.keys())

            # Allow the user to select a specific exam
            selected_exam = st.selectbox(
                "Select an exam", ["Select an exam"] + exam_names
            )

            start_prn = st.number_input(
                "Enter Start PRN:", min_value=0, value=None, key="start_prn"
            )
            end_prn = st.number_input(
                "Enter End PRN:", min_value=0, value=None, key="end_prn"
            )

            data = None
            exam_id = None

            if st.button("Run Scraping"):
                if selected_exam == "Select an exam":
                    st.warning("Select an exam")
                    return
                if start_prn is None or end_prn is None:
                    st.warning("Enter valid numeric PRN's")
                    return
                with st.spinner("Scraping in progress..."):
                    if end_prn < start_prn:  # swap the input prn's if end_prn is bigger
                        start_prn, end_prn = end_prn, start_prn
                    exam_id = selected_semester_data[selected_exam]
                    if selected_category == "UG":
                        data = scrape_results(exam_id, start_prn, end_prn)
                    elif selected_category == "PG":
                        data = scrape_results_pg(exam_id, start_prn, end_prn)

                    if data is None:
                        st.error(
                            "Error: Failed to retrieve data. Please check your inputs."
                        )
                        return

                    if len(data) <= 1:
                        st.error(
                            "Error: No data found. Check the entered register numbers or exam."
                        )
                        return

                st.success("Scraping complete!")

            # Display download button below the "Run Scraping" button
            if data:
                st.info(
                    "Hover over the table below to find the download button for CSV."
                )

                df = pd.DataFrame(data[1:], columns=data[0])
                st.dataframe(df, hide_index=True)


if __name__ == "__main__":
    main()
