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


def get_student_sem_overall_result(overall_html):
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


def get_student_sem_result(html):
    """Parse HTML and extract student semester results."""
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
    sem_overall_result = get_student_sem_overall_result(sem_overall_result_tr)
    subjects_results = get_student_subjects_results(sem_subject_rows)

    return {
        "personal_details": student_details,
        "overall_result": sem_overall_result,
        "subjects_results": subjects_results,
    }


def main():
    # Sample data
    url_ug = "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/"
    exam_id = "113"
    start_prn = "220021082830"
    end_prn = "220021082870"

    for prn in range(int(start_prn), int(end_prn)):

        html_data = get_html_data(url_ug, exam_id, str(prn))

        student_result = get_student_sem_result(html_data)

        print(student_result)


if __name__ == "__main__":
    main()
