import requests
import re
from bs4 import BeautifulSoup


def get_html_data(url, exam_id, prn):
    """Fetch HTML data from the specified URL using given exam ID and PRN."""
    payload = {"exam_id": exam_id, "prn": prn, "btnresult": "Get Result"}
    return requests.post(url, data=payload).content


def get_student_details(student_details_table):
    """Extract student personal details from the HTML table."""
    prn = student_details_table.select(
        "td:-soup-contains('Permanent Register Number:') + td + td"
    )[0].get_text(strip=True)

    name = student_details_table.select(
        "td:-soup-contains('Name of Student:') + td + td"
    )[0].get_text(strip=True)

    program = student_details_table.select("td:-soup-contains('Programme:') + td + td")[
        0
    ].get_text(strip=True)

    exam_centre = student_details_table.select(
        "td:-soup-contains('Exam Centre:') + td + td"
    )[0].get_text(strip=True)

    return {"prn": prn, "name": name, "program": program, "exam_centre": exam_centre}


def get_student_curr_sem_overall_result(overall_html):
    """Extract overall student semester result details from the HTML."""
    total_credit = overall_html.select("td:nth-child(2)")[0].get_text(strip=True)
    scpa_string = overall_html.select("td:-soup-contains('SCPA')")[0].get_text(
        strip=True
    )
    scpa_num = re.findall(r"\d+\.\d+", scpa_string)

    scpa = scpa_num[0] if scpa_num else "---"

    total_marks = overall_html.select("td:-soup-contains('SCPA') + td")[0].get_text(
        strip=True
    )
    max_marks = overall_html.select("td:-soup-contains('SCPA') + td + td")[0].get_text(
        strip=True
    )
    grade = overall_html.select("td:-soup-contains('SCPA') + td + td + td")[0].get_text(
        strip=True
    )
    cp = overall_html.select("td:nth-last-child(2)")[0].get_text(strip=True)
    result = overall_html.select("td:last-child")[0].get_text(strip=True)

    return {
        "total_credit": total_credit,
        "scpa": scpa,
        "total_marks": total_marks,
        "max_marks": max_marks,
        "grade": grade,
        "cp": cp,
        "result": result,
    }


def get_student_subjects_results(sem_subject_rows):
    """Extract individual subject results from the HTML rows."""
    subjects_data = []

    for tr in sem_subject_rows:
        sub_data = {}

        tds = tr.select("td")

        sub_data["course_code"] = tds[0].get_text(strip=True)
        sub_data["course"] = tds[1].get_text(strip=True)
        sub_data["credit"] = tds[2].get_text(strip=True)
        sub_data["esa_ext"] = tds[3].get_text(strip=True)
        sub_data["max_ext"] = tds[4].get_text(strip=True)
        sub_data["isa_int"] = tds[5].get_text(strip=True)
        sub_data["max_int"] = tds[6].get_text(strip=True)
        sub_data["total"] = tds[7].get_text(strip=True)
        sub_data["max"] = tds[8].get_text(strip=True)
        sub_data["grade"] = tds[9].get_text(strip=True)
        sub_data["gp"] = tds[10].get_text(strip=True)
        sub_data["cp"] = tds[11].get_text(strip=True)
        sub_data["result"] = tds[12].get_text(strip=True)

        subjects_data.append(sub_data)

    return subjects_data


def get_student_sem_wise_results(html_table):
    """Extract semester-wise results from the HTML table."""
    sem_result_rows = html_table.select("tr")[1:]
    sem_wise_results = []

    for tr in sem_result_rows:
        sem_result = {}

        tds = tr.select("td")

        sem_result["sem"] = tds[0].get_text(strip=True)
        sem_result["credit"] = tds[1].get_text(strip=True)
        sem_result["scpa"] = tds[2].get_text(strip=True)
        sem_result["grade"] = tds[3].get_text(strip=True)
        sem_result["result"] = tds[4].get_text(strip=True)
        sem_result["pass_time"] = tds[5].get_text(strip=True)

        sem_wise_results.append(sem_result)

    return sem_wise_results


def get_final_result(table_html):
    """Extract the final result details from the HTML table."""
    final_result = {}

    tds = table_html.select("tr")[-1].select("td")

    final_result["marks_awarded"] = tds[0].get_text(strip=True)
    final_result["max_marks"] = tds[1].get_text(strip=True)
    final_result["ccpa"] = tds[2].get_text(strip=True)
    final_result["total_credit_point"] = tds[3].get_text(strip=True)
    final_result["programme_credit"] = tds[4].get_text(strip=True)
    final_result["grade"] = tds[5].get_text(strip=True)
    final_result["result"] = tds[6].get_text(strip=True)

    return final_result


def get_programme_part_result(trs):
    """Extract programme part results from the HTML rows."""
    programme_part_result = []

    for tr in trs:
        programme_part = {}

        tds = tr.select("td")

        programme_part["part"] = tds[0].get_text(strip=True)
        programme_part["marks"] = tds[1].get_text(strip=True)
        programme_part["max_marks"] = tds[2].get_text(strip=True)
        programme_part["ccpa"] = tds[3].get_text(strip=True)
        programme_part["credits"] = tds[4].get_text(strip=True)
        programme_part["grade"] = tds[5].get_text(strip=True)

        programme_part_result.append(programme_part)

    return programme_part_result


def get_student_result(html):
    """Parse HTML and extract student semester results and final result if exists."""
    soup = BeautifulSoup(html, "html.parser")

    if not soup.select(".frame"):
        return None

    sem_result_table = soup.select(".frame > table")[1]

    student_details_table = soup.select(".frame > table")[0]
    sem_overall_result_tr = sem_result_table.select("tr[height='30']")[0]
    sem_subject_rows = sem_result_table.select(
        "tr:nth-child(n+3):not(:nth-last-child(-n + 5))"
    )

    student_details = get_student_details(student_details_table)
    sem_overall_result = get_student_curr_sem_overall_result(sem_overall_result_tr)
    subjects_results = get_student_subjects_results(sem_subject_rows)

    student_result = {
        "personal_details": student_details,
        "overall_sem_result": sem_overall_result,
        "subjects_results": subjects_results,
    }

    all_sem_results_table = soup.select(
        "legend:-soup-contains('SEMESTER RESULTS') + table"
    )

    if all_sem_results_table:
        sem_wise_results = get_student_sem_wise_results(all_sem_results_table[0])
        student_result["sem_wise_result"] = sem_wise_results

    final_result_table = soup.select(
        "table[style='width:500px;']:-soup-contains('CCPA')"
    )

    if final_result_table:
        final_result = get_final_result(final_result_table[0])
        student_result["final_result"] = final_result

    programme_part_trs = soup.select(
        "tr:-soup-contains('PROGRAMME PART RESULTS') ~ tr:has(>td[height='25'])"
    )

    if programme_part_trs:
        program_part_result = get_programme_part_result(programme_part_trs)
        student_result["programme_part_result"] = program_part_result

    return student_result


def get_results(url, exam_id, start_prn, end_prn, pg=False):
    results = []

    for prn in range(int(start_prn), int(end_prn) + 1):
        html_data = get_html_data(url, exam_id, str(prn))
        student_result = get_student_result(html_data)

        results.append(student_result)

    return results
