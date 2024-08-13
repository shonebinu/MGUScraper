import streamlit as st
import altair as alt
from scraper.result_scraper import get_results
from scraper.metadata_scraper import get_exam_metadata


def main():
    st.set_page_config(page_title="MGU Scraper", page_icon="../favicon.ico")
    st.title("MGU Scraper")

    st.info(
        "Note: The data provided by this app belongs to the respective university. Please ensure you have permission from the data owner before using this tool."
    )

    st.info(
        "This webapp is made for scraping the UG results of MGU examinations. PG scraping hasn't been implemented yet."
    )

    st.info("Course end result for sixth sem is under work" )

    semesters = [
        "FIRST SEMESTER",
        "SECOND SEMESTER",
        "THIRD SEMESTER",
        "FOURTH SEMESTER",
        "FIFTH SEMESTER",
        "SIXTH SEMESTER",
    ]

    selected_semester = st.selectbox(
        "Select a semester",
        semesters,
        index=None,
        placeholder="Select a semester...",
        format_func=lambda x: f"Semester {semesters.index(x) + 1}",
    )

    if selected_semester:
        selected_semester_exams = get_exam_metadata(
            "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/",
            semesters,
        )[selected_semester]

        selected_exam_id = st.selectbox(
            "Select an exam",
            [exam["exam_id"] for exam in selected_semester_exams],
            index=None,
            placeholder="Select an exam...",
            format_func=lambda exam_id: " ".join(
                next(
                    (
                        exam["exam_name"]
                        for exam in selected_semester_exams
                        if exam["exam_id"] == exam_id
                    )
                ).split()[2:]
            ),
        )

        start_prn = st.number_input(
            "Enter Start PRN", min_value=0, value=None, placeholder="Enter Start PRN..."
        )
        end_prn = st.number_input(
            "Enter End PRN", min_value=0, value=None, placeholder="Enter End PRN..."
        )

        if st.button("Run Scraping"):
            if not selected_exam_id or not start_prn or not end_prn:
                st.warning("Fill up all the required fields")
                return

            if end_prn < start_prn:
                st.warning("Start PRN should be less than End PRN")
                return

            with st.spinner("Scraping in progress..."):
                data = get_results(
                    "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/",
                    selected_exam_id,
                    start_prn,
                    end_prn,
                )

                if not data:
                    st.warning("Data doesn't exist for the given parameters. Please check the given inputs" )
                    return

                st.success("Scraping complete!")

                st.caption(
                    f"Semester {semesters.index(selected_semester) + 1}"
                    + " results for the given range of PRN"
                )

                st.info(
                    "Hover over the table's to find the download button for CSV file."
                )

                extracted_data = extract_major_fields(data)

                for program_wise_result in extracted_data:
                    st.markdown(f"**{program_wise_result}**")
                    display_results_table_and_charts(extracted_data[program_wise_result])


def display_results_table_and_charts(data):
    st.dataframe(data)
    bar_chart_data = get_bar_chart_data(data)
    st.altair_chart(get_grade_distribution_chart_data(bar_chart_data), use_container_width=True)

def extract_major_fields(data):
    program_wise_flattened_result = {}

    for d in data:
        if d:
            program = d["personal_details"]["program"]

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
            
    return program_wise_flattened_result


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


if __name__ == "__main__":
    main()
