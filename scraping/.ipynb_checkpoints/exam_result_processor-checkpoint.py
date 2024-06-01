from scrapy import Selector
import requests
import re
import numpy as np


def fetch_html(url, payload):
    try:
        html = requests.post(url, data=payload).content
        return html
    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return None


def extract_mark_rows(garbage_rows):
    i = -1
    for row_selector in garbage_rows:
        i = i + 1
        height_attribute = row_selector.xpath("@height").extract_first()
        if height_attribute == "30":
            break
    return garbage_rows[2 : i + 1]


def extract_student_info(sel, name_xpath, prn_xpath):
    current_prn = sel.xpath(prn_xpath).extract_first()
    name = sel.xpath(name_xpath).extract_first()
    return current_prn, name


def extract_result_array(mark_rows):
    result_array = []
    for row in mark_rows:
        inner_array = []
        for td_element in row.xpath(".//td"):
            inner_array.append(td_element.xpath("normalize-space()").extract_first())
        result_array.append(inner_array)
    return result_array


def extract_scpa(match):
    return str(float(match.group())) if match else "---"


def scrape_results(exam_id, start_prn, end_prn, selected_semester):
    url = "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/"
    payload_template = {"exam_id": str(exam_id), "prn": "", "btnresult": "Get Result"}

    data = []
    result_array = []
    final_result = []
    for prn in range(start_prn, end_prn + 1):
        payload = {**payload_template, "prn": str(prn)}

        html = fetch_html(url, payload)
        if html is None:
            continue

        sel = Selector(text=html)
        garbage_rows = sel.xpath('//*[@class="frame"]').xpath("./table[2]//tr")
        if not garbage_rows:
            continue

        mark_rows = extract_mark_rows(garbage_rows)
        result_array = extract_result_array(mark_rows)

        current_prn, name = extract_student_info(
            sel,
            '//*[@style="font-size:14px;color:#936;"]/text()',
            '//*[@id="prn"]/@value',
        )
        if not name:
            continue

        student_row = [current_prn, name]

        for row in result_array[:-1]:
            student_row += [row[5], row[3], row[7], row[9]]

        overall = result_array[-1]

        match = re.search(r"\d+\.\d+|\d+", overall[2])
        scpa = extract_scpa(match)

        student_row += [scpa, overall[3], overall[5]]

        data.append(student_row)

        # extract final sem extra results
        if selected_semester == "Semester 6":
            additional_rows = sel.xpath('(//*[@class="green_frame"])[2]//table//tr')
            additional_data = []

            if additional_rows:

                for row in additional_rows[2:]:
                    td_elements = row.xpath(".//td")
                    for td in td_elements:
                        if td.xpath("normalize-space()").extract_first() not in [
                            "SEMESTER I",
                            "SEMESTER II",
                            "SEMESTER III",
                            "SEMESTER IV",
                            "SEMESTER V",
                            "SEMESTER VI",
                        ]:
                            additional_data.append(
                                td.xpath("normalize-space()").extract_first()
                            )

                overall_result = sel.xpath(
                    '(//*[@class="green_frame"])[3]//table//tr[3]'
                )

                for i in range(len(overall_result)):
                    row = overall_result[i]
                    td_elements = row.xpath(".//td")
                    td_data_row = []
                    for td in td_elements:
                        td_data = td.xpath("normalize-space()").extract_first()
                        td_data_row.append(td_data)
                    additional_data.extend(td_data_row)

                final_result.append(additional_data)

            else:

                final_result.append([])
        # extract final sem extra results END

    header = []
    for row in result_array[:-1]:
        header += [
            row[0] + " ISA",
            row[0] + " ESA",
            row[0] + " Total",
            row[0] + " Grade",
        ]
    header = ["PRN", "Name"] + header + ["SCPA", "Total Mark", "Grade"]

    if selected_semester == "Semester 6":

        for i in range(len(data)):
            final_result[i].insert(0, data[i][0])
            final_result[i].insert(1, data[i][1])

        add_header = [
            "PRN",
            "Name",
            "Semester 1 Credits",
            "Semester 1 SCPA",
            "Semester 1 Grade",
            "Semester 1 Result",
            "Semester 1 Pass Time",
            "Semester 2 Credits",
            "Semester 2 SCPA",
            "Semester 2 Grade",
            "Semester 2 Result",
            "Semester 2 Pass Time",
            "Semester 3 Credits",
            "Semester 3 SCPA",
            "Semester 3 Grade",
            "Semester 3 Result",
            "Semester 3 Pass Time",
            "Semester 4 Credits",
            "Semester 4 SCPA",
            "Semester 4 Grade",
            "Semester 4 Result",
            "Semester 4 Pass Time",
            "Semester 5 Credits",
            "Semester 5 SCPA",
            "Semester 5 Grade",
            "Semester 5 Result",
            "Semester 5 Pass Time",
            "Semester 6 Credits",
            "Semester 6 SCPA",
            "Semester 6 Grade",
            "Semester 6 Result",
            "Semester 6 Pass Time",
            "Total Marks Awarded",
            "Maximum Marks",
            "CCPA",
            "Total Credit Points",
            "Programme Credits",
            "Final Grade",
            "Final Result",
        ]

        final_result.insert(0, add_header)

    data.insert(0, header)

    if len(data) < 2:
        return None

    return {"sem_result": data, "final_result": final_result}


# PG


def scrape_results_pg(exam_id, s_prn, e_prn, selected_semester):
    url = "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/PGResultViewSec_ctrl/"
    students_marks = []
    for_head = None
    for prn in range(s_prn, e_prn + 1):
        data = {
            "exam_id": str(exam_id),
            "prn": str(prn),
            "btnresult": "Get Result",
        }
        html = requests.post(url, data=data).content
        sel = Selector(text=html)
        garbage_rows = sel.xpath("//*[@class='bord_rslt']/parent::*")
        if not garbage_rows:
            continue
        result_array = []
        name = sel.xpath(
            '//*[@class="frame"]/table//table//tr[2]/td[3]/text()'
        ).extract_first()
        student_row = [str(prn), name]

        for row in garbage_rows[2:-1]:
            inner_array = []
            for td_element in row.xpath(".//td"):
                inner_array.append(
                    td_element.xpath("normalize-space()").extract_first()
                )
            result_array.append(inner_array)
            if not for_head:
                for_head = result_array

        for row in result_array:
            student_row += [row[2], row[3], row[4], row[5], row[6], row[7]]

        overall_gpa = garbage_rows[-1].xpath("./td[7]//text()").extract_first()
        overall_grade = garbage_rows[-1].xpath("./td[8]//text()").extract_first()
        student_row += [overall_gpa, overall_grade]
        students_marks.append(student_row)

    header = ["PRN", "Name"]
    for row in for_head:
        header += [
            row[0] + " Theory INT",
            row[0] + " Theory EXT",
            row[0] + " Practical INT",
            row[0] + " Practical EXT",
            row[0] + " GPA",
            row[0] + " Grade",
        ]

    students_marks = [header + ["Overall GPA"] + ["Overall Grade"]] + students_marks

    if len(students_marks) < 2:
        return None

    return {"sem_result": students_marks, "final_result": []}
