import streamlit as st
import altair as alt
import asyncio
from scraper.result_scraper import get_results
from scraper.metadata_scraper import get_exam_metadata
from utils.data_formatting import extract_sem_results_categorized_on_program
from utils.data_formatting import extract_courses_details_categorized_on_program
from utils.data_formatting import extract_bar_chart_data
from utils.data_formatting import extract_programme_end_final_result
from utils.data_formatting import extract_programme_end_semester_results
from utils.data_formatting import extract_programme_end_final_results_bar_chart_data


SEMESTERS = [
    "FIRST SEMESTER",
    "SECOND SEMESTER",
    "THIRD SEMESTER",
    "FOURTH SEMESTER",
    "FIFTH SEMESTER",
    "SIXTH SEMESTER",
]


def main():
    show_info()

    selected_semester = select_semester(SEMESTERS)

    try:
        semester_exam_metadata = get_exam_metadata(
            "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/",
            SEMESTERS,
        )
    except Exception:
        st.info(
            "Unable to fetch exam data at the moment. Please check the host's website or try again later."
        )
        return

    if not selected_semester:
        return

    selected_exam_id = select_exam(semester_exam_metadata[selected_semester])

    start_prn, end_prn = select_prn_range()

    if not st.button("Run Scraping", type="primary"):
        return

    if not all([selected_exam_id, start_prn, end_prn]):
        st.warning("Fill up all the required fields")
        return

    if end_prn < start_prn:
        st.warning("Start PRN should be less than End PRN")
        return

    if end_prn - start_prn > 100000:
        st.warning("The range between Start PRN and End PRN is too large")
        return

    try:
        data = asyncio.run(
            get_results(
                "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/",
                selected_exam_id,
                start_prn,
                end_prn,
            )
        )
    except Exception:
        st.info(
            "Unable to retrieve results at the moment. Please check the host's website or recheck your parameters again"
        )
        return

    st.markdown("")

    display_scraped_data(data, selected_semester)


def show_info():
    st.title("MGU Scraper")
    st.warning(
        "Note: The data provided by this app belongs to the respective university. Please ensure you have permission from the data owner before using this tool."
    )


def select_semester(SEMESTERS):
    return st.selectbox(
        "Select a semester",
        SEMESTERS,
        index=None,
        placeholder="Select a semester...",
        format_func=lambda x: f"Semester {SEMESTERS.index(x) + 1}",
    )


def select_exam(semester_exams):
    return st.selectbox(
        "Select an exam",
        [exam["exam_id"] for exam in semester_exams],
        index=None,
        placeholder="Select an exam...",
        format_func=lambda exam_id: " ".join(
            next(
                (
                    exam["exam_name"]
                    for exam in semester_exams
                    if exam["exam_id"] == exam_id
                )
            ).split()[2:]
        ),
    )


def select_prn_range():
    start_prn = st.number_input(
        "Enter Start PRN", min_value=0, value=None, placeholder="Enter Start PRN..."
    )
    end_prn = st.number_input(
        "Enter End PRN", min_value=0, value=None, placeholder="Enter End PRN..."
    )
    return start_prn, end_prn


def display_scraped_data(scraped_data, selected_semester):
    if not scraped_data:
        st.warning(
            "Data doesn't exist for the given parameters. Please check the given inputs",
        )
        return

    st.info("Hover over the table's to find the download button for CSV file.")

    sem_results_categorized_on_program = extract_sem_results_categorized_on_program(
        scraped_data
    )
    course_details_categorized_on_program = (
        extract_courses_details_categorized_on_program(scraped_data)
    )

    for program in sem_results_categorized_on_program:
        display_scraped_data_of_one_program(
            selected_semester,
            program,
            sem_results_categorized_on_program[program],
            course_details_categorized_on_program[program],
        )

        if selected_semester == SEMESTERS[-1]:
            programme_end_final_result = extract_programme_end_final_result(
                scraped_data
            )
            programme_end_semester_wise_result = extract_programme_end_semester_results(
                scraped_data
            )

            display_programme_end_datas_of_one_program(
                programme_end_final_result, programme_end_semester_wise_result
            )


def display_scraped_data_of_one_program(
    selected_semester, program, sem_studs_result, sem_courses_data
):
    st.markdown("")
    st.markdown(
        f"##### *{program} ({len(sem_studs_result)} nos)*",
        unsafe_allow_html=True,
    )
    st.markdown("<u>**Semester Results**</u>", unsafe_allow_html=True)
    st.dataframe(sem_studs_result)

    bar_chart_data = extract_bar_chart_data(sem_studs_result)
    st.altair_chart(
        get_grade_distribution_chart_data(bar_chart_data), use_container_width=True
    )

    st.markdown(f"**{selected_semester} Course Details**")
    st.dataframe(sem_courses_data)


def get_grade_distribution_chart_data(bar_chart_data):
    color_mapping = {
        "S": "#d946ef",
        "O": "#d946ef",
        "A+": "#2563eb",
        "A": "#60a5fa",
        "B+": "#059669",
        "B": "#34d399",
        "C": "#fde047",
        "D": "#fca5a5",
        "P": "#fca5a5",
        "Fail": "#1f2937",
    }

    return (
        alt.Chart(
            alt.Data(
                values=[
                    {"Grade": grade, "Count": count}
                    for grade, count in bar_chart_data.items()
                ]
            )
        )
        .mark_bar()
        .encode(
            x=alt.X("Grade:N", sort=list(bar_chart_data.keys())),
            y="Count:Q",
            color=alt.Color(
                "Grade:N",
                scale=alt.Scale(
                    domain=list(color_mapping.keys()),
                    range=list(color_mapping.values()),
                ),
                legend=None,
            ),
        )
        .properties(title="Grade Distribution")
    )


def display_programme_end_datas_of_one_program(final_result, semester_wise_results):
    st.markdown("---")

    st.markdown("<u>**Programme End Final Results**</u>", unsafe_allow_html=True)
    st.caption("Students with none in the field may have ongoing supplies")

    st.dataframe(final_result)
    bar_chart_data = extract_programme_end_final_results_bar_chart_data(final_result)

    st.altair_chart(
        get_grade_distribution_chart_data(bar_chart_data), use_container_width=True
    )

    st.markdown("**Semester Wise Results**")
    st.dataframe(semester_wise_results)


if __name__ == "__main__":
    main()
