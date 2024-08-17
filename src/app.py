import streamlit as st
import altair as alt
from scraper.result_scraper import get_results
from scraper.metadata_scraper import get_exam_metadata

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

    if not selected_semester:
        return

    # TODO: Implement try catch
    selected_exam_id = select_exam(
        semester_exams=get_exam_metadata(
            "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/",
            SEMESTERS,
        )[selected_semester]
    )

    start_prn, end_prn = select_prn_range()

    if not st.button("Run Scraping"):
        return

    if not all([selected_exam_id, start_prn, end_prn]):
        st.warning("Fill up all the required fields")
        return

    if end_prn < start_prn:
        st.warning("Start PRN should be less than End PRN")
        return

    with st.spinner("Scraping in progress..."):
        # TODO: Implement try catch
        data = get_results(
            "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/",
            selected_exam_id,
            start_prn,
            end_prn,
        )

        display_scraped_data(data, selected_semester)


def show_info():
    st.title("MGU Scraper")
    st.info(
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
            "Data doesn't exist for the given parameters. Please check the given inputs"
        )
        return

    display_scraped_data_header_info(selected_semester)

    # Refactor from here
    extracted_data, coursecode_to_coursename = extract_major_fields(scraped_data)

    for program in extracted_data:
        display_results_table_and_charts(
            program,
            extracted_data[program],
            coursecode_to_coursename[program],
        )


def display_scraped_data_header_info(selected_semester):
    st.success("Scraping complete!")
    st.caption(
        f"Semester {SEMESTERS.index(selected_semester) + 1}"
        + " results for the given range of PRN"
    )
    st.info("Hover over the table's to find the download button for CSV file.")


def display_results_table_and_charts(program_name, student_data, coursecode_to_name):
    st.markdown(
        f"###### <u>{program_name} ({len(student_data)} Entries)</u>",
        unsafe_allow_html=True,
    )
    st.dataframe(student_data)

    st.markdown(f"**Course Details**")
    st.dataframe(coursecode_to_name)

    bar_chart_data = get_bar_chart_data(student_data)
    st.altair_chart(
        get_grade_distribution_chart_data(bar_chart_data), use_container_width=True
    )


def extract_major_fields(data):
    program_wise_flattened_result = {}
    coursecode_to_coursename_map = {}

    for d in data:
        if d:
            program = d["personal_details"]["program"]

            if program not in coursecode_to_coursename_map:
                coursecode_to_coursename_map[program] = []
                for x in d["subjects_results"]:
                    course_code = x["course_code"]
                    course_name = x["course"]
                    credit = x["credit"]
                    max_external = x["max_ext"]
                    max_internal = x["max_int"]
                    max = x["max"]
                    coursecode_to_coursename_map[program].append(
                        {
                            "Course Code": course_code,
                            "Course Name": course_name,
                            "Credit": credit,
                            "Max Internal": max_internal,
                            "Max External": max_external,
                            "Max Marks": max,
                        }
                    )

            temp = {}
            temp["PRN"] = d["personal_details"]["prn"]
            temp["Name"] = d["personal_details"]["name"]
            temp["Exam centre"] = d["personal_details"]["exam_centre"]

            for x in d["subjects_results"]:
                course = x["course_code"]
                temp[f"{course} ISA"] = x["isa_int"]
                temp[f"{course} ESA"] = x["esa_ext"]
                temp[f"{course} Total"] = x["total"]
                temp[f"{course} Grade"] = x["grade"]

            temp["SCPA"] = d["overall_sem_result"]["scpa"]
            temp["Total Mark"] = d["overall_sem_result"]["total_marks"]
            temp["Grade"] = d["overall_sem_result"]["grade"]

            if program not in program_wise_flattened_result:
                program_wise_flattened_result[program] = []

            program_wise_flattened_result[program].append(temp)

    for x in coursecode_to_coursename_map:
        program_row = coursecode_to_coursename_map[x]

        sum_credit = 0
        sum_max_internal = 0
        sum_max_external = 0
        sum_max_marks = 0

        for i in program_row:
            sum_credit += int(i["Credit"])
            sum_max_internal += int(i["Max Internal"])
            sum_max_external += int(i["Max External"])
            sum_max_marks += int(i["Max Marks"])

        program_row.append(
            {
                "Course Code": "Total",
                "Course Name": "",
                "Credit": str(sum_credit),
                "Max Internal": str(sum_max_internal),
                "Max External": str(sum_max_external),
                "Max Marks": str(sum_max_marks),
            }
        )

    return (program_wise_flattened_result, coursecode_to_coursename_map)


def get_bar_chart_data(data):
    grades_order = ["S", "A+", "A", "B+", "B", "C", "D", "Fail"]
    grade_count = {}

    for d in data:
        student_grade = d["Grade"] if d["Grade"] != "---" else "Fail"

        if student_grade in grade_count:
            grade_count[student_grade] += 1
        else:
            grade_count[student_grade] = 1

    # Convert the dictionary to a list of tuples and sort it in place
    grade_count_items = list(grade_count.items())
    grade_count_items.sort(key=lambda x: grades_order.index(x[0]))

    # Convert the sorted list of tuples back to a dictionary
    sorted_grade_count = dict(grade_count_items)

    return sorted_grade_count


def get_grade_distribution_chart_data(bar_chart_data):
    color_mapping = {
        "S": "#d946ef",
        "A+": "#2563eb",
        "A": "#60a5fa",
        "B+": "#059669",
        "B": "#34d399",
        "C": "#fde047",
        "D": "#fca5a5",
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
            ),
        )
        .properties(title="Grade Distribution")
    )
