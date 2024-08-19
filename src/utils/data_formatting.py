def extract_sem_results_categorized_on_program(scraped_data):
    """Extract students sem results categorized on program"""
    results_categorized_on_program = {}
    for stud_data in scraped_data:
        if not stud_data:
            continue

        program = stud_data["personal_details"]["program"]
        if program not in results_categorized_on_program:
            results_categorized_on_program[program] = []

        major_fields = extract_sem_results_major_fields(stud_data)
        results_categorized_on_program[program].append(major_fields)

    return results_categorized_on_program


def extract_sem_results_major_fields(stud_data):
    """Extract major fields of a students sem results"""
    major_fields = {}
    major_fields["PRN"] = stud_data["personal_details"]["prn"]
    major_fields["Name"] = stud_data["personal_details"]["name"]
    major_fields["Exam centre"] = stud_data["personal_details"]["exam_centre"]

    for sub_data in stud_data["subjects_results"]:
        course = sub_data["course_code"]
        if "OPT" in course:
            course = "Open Course"
            major_fields["Open Course"] = (
                f"{sub_data['course_code']}: {sub_data['course']}"
            )
        major_fields[f"{course} ISA"] = sub_data["isa_int"]
        major_fields[f"{course} ESA"] = sub_data["esa_ext"]
        major_fields[f"{course} Total"] = sub_data["total"]
        major_fields[f"{course} Grade"] = sub_data["grade"]

    major_fields["SCPA"] = stud_data["overall_sem_result"]["scpa"]
    major_fields["Total Mark"] = stud_data["overall_sem_result"]["total_marks"]
    major_fields["Grade"] = stud_data["overall_sem_result"]["grade"]

    return major_fields


def extract_courses_details_categorized_on_program(scraped_data):
    """Categorize course details based on the program"""
    course_details_categorized_on_program = {}
    for stud_data in scraped_data:
        if not stud_data:
            continue

        program = stud_data["personal_details"]["program"]

        if program in course_details_categorized_on_program:
            continue

        course_details = extract_course_details(stud_data)
        course_details_categorized_on_program[program] = course_details

    return course_details_categorized_on_program


def extract_course_details(stud_data):
    """Extract course details for a given student's data"""
    course_details = []
    for sub_data in stud_data["subjects_results"]:
        course_code = sub_data["course_code"]
        course_name = sub_data["course"]
        credit = sub_data["credit"]
        max_external = sub_data["max_ext"]
        max_internal = sub_data["max_int"]
        max_marks = sub_data["max"]

        course_details.append(
            {
                "Course Code": "Open Course" if "OPT" in course_code else course_code,
                "Course Name": "Open Course" if "OPT" in course_code else course_name,
                "Credit": credit,
                "Max Internal": max_internal,
                "Max External": max_external,
                "Max Marks": max_marks,
            }
        )
    course_details.append(calculate_courses_totals(course_details))

    return course_details


def calculate_courses_totals(course_details):
    """Calculate total credit, internal, external numerics of all courses combined in a sem"""
    total_credit = 0
    total_max_internal = 0
    total_max_external = 0
    total_max_marks = 0
    for course in course_details:
        total_credit += safe_int(course["Credit"])
        total_max_internal += safe_int(course["Max Internal"])
        total_max_external += safe_int(course["Max External"])
        total_max_marks += safe_int(course["Max Marks"])

    return {
        "Course Code": "Total",
        "Course Name": f"{len(course_details)} nos",
        "Credit": str(total_credit),
        "Max Internal": str(total_max_internal),
        "Max External": str(total_max_external),
        "Max Marks": str(total_max_marks),
    }


def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def extract_bar_chart_data(data):
    """Get bar chart data on Grade(x) to Students(y) for semester result"""
    grades_order = ["S", "O", "A+", "A", "B+", "B", "C", "D", "P", "Fail"]
    grade_count = {grade: 0 for grade in grades_order}

    for d in data:
        student_grade = d["Grade"] if d["Grade"] != "---" else "Fail"
        grade_count[student_grade] += 1

    return {
        grade: grade_count[grade] for grade in grades_order if grade_count[grade] > 0
    }


def extract_programme_end_final_result(scraped_data):
    """Extract programme end final result of the student"""
    final_result = []
    for stud in scraped_data:
        if "final_result" not in stud:
            final_result.append(
                {
                    "PRN": stud["personal_details"]["prn"],
                    "Name": stud["personal_details"]["name"],
                }
            )
            continue

        row = stud["final_result"]
        final_result.append(
            {
                "PRN": stud["personal_details"]["prn"],
                "Name": stud["personal_details"]["name"],
                **{
                    key.replace("_", " ").title() if key != "ccpa" else "CCPA": value
                    for key, value in row.items()
                },
            }
        )

    return final_result


def extract_programme_end_semester_results(scraped_data):
    """Extract programme end semester wise results of the student"""
    final_sem_wise_result = []
    for stud in scraped_data:
        if "sem_wise_result" not in stud:
            final_sem_wise_result.append(
                {
                    "PRN": stud["personal_details"]["prn"],
                    "Name": stud["personal_details"]["name"],
                }
            )
            continue

        sem_wise_result = stud["sem_wise_result"]
        temp = {}
        for i, sem in enumerate(sem_wise_result, start=1):
            temp["PRN"] = stud["personal_details"]["prn"]
            temp["Name"] = stud["personal_details"]["name"]

            temp[f"SEM {i} Credit"] = sem["credit"]
            temp[f"SEM {i} SCPA"] = sem["scpa"]
            temp[f"SEM {i} Grade"] = sem["grade"]
            temp[f"SEM {i} Result"] = sem["result"]
            temp[f"SEM {i} Pass Time"] = sem["pass_time"]

        final_sem_wise_result.append(temp)

    return final_sem_wise_result


def extract_programme_end_final_results_bar_chart_data(data):
    """Get bar chart data on Grade(x) to Students(y) on programme end final result"""
    grades_order = ["S", "O", "A+", "A", "B+", "B", "C", "D", "P", "Fail"]
    grade_count = {grade: 0 for grade in grades_order}

    for d in data:
        student_grade = d["Grade"] if "Grade" in d else "Fail"
        grade_count[student_grade] += 1

    return {
        grade: grade_count[grade] for grade in grades_order if grade_count[grade] > 0
    }
