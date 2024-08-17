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
                "Course Code": course_code,
                "Course Name": course_name,
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
        total_credit += int(course["Credit"])
        total_max_internal += int(course["Max Internal"])
        total_max_external += int(course["Max External"])
        total_max_marks += int(course["Max Marks"])

    return {
        "Course Code": "Total",
        "Course Name": f"{len(course_details)} nos",
        "Credit": str(total_credit),
        "Max Internal": str(total_max_internal),
        "Max External": str(total_max_external),
        "Max Marks": str(total_max_marks),
    }


def extract_bar_chart_data(data):
    """Get bar chart data on Grade(x) to Students(y)"""
    grades_order = ["S", "A+", "A", "B+", "B", "C", "D", "Fail"]
    grade_count = {grade: 0 for grade in grades_order}

    for d in data:
        student_grade = d["Grade"] if d["Grade"] != "---" else "Fail"
        grade_count[student_grade] += 1

    return {
        grade: grade_count[grade] for grade in grades_order if grade_count[grade] > 0
    }
