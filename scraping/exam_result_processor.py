from scrapy import Selector
import requests
import re

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
        height_attribute = row_selector.xpath('@height').extract_first()
        if height_attribute == '30':
            break
    return garbage_rows[2:i + 1]

def extract_student_info(sel, name_xpath, prn_xpath):
    current_prn = sel.xpath(prn_xpath).extract_first()
    name = sel.xpath(name_xpath).extract_first()
    return current_prn, name

def extract_result_array(mark_rows):
    result_array = []
    for row in mark_rows:
        inner_array = []
        for td_element in row.xpath('.//td'):
            inner_array.append(td_element.xpath('normalize-space()').extract_first())
        result_array.append(inner_array)
    return result_array

def extract_scpa(match):
    return str(float(match.group())) if match else '---'

def scrape_results(url, exam_id, start_prn, end_prn):
    payload_template = {'exam_id': str(exam_id), 'prn': '', 'btnresult': 'Get Result'}

    data = []
    result_array = []
    for prn in range(start_prn, end_prn + 1):
        payload = {**payload_template, 'prn': str(prn)}

        html = fetch_html(url, payload)
        if html is None:
            continue

        sel = Selector(text=html)
        garbage_rows = sel.xpath('//*[@class="frame"]').xpath('./table[2]//tr')
        if not garbage_rows:
            continue

        mark_rows = extract_mark_rows(garbage_rows)
        result_array = extract_result_array(mark_rows)

        current_prn, name = extract_student_info(sel, '//*[@style="font-size:14px;color:#936;"]/text()', '//*[@id="prn"]/@value')
        if not name:
            continue

        student_row = [current_prn, name]

        for row in result_array[:-1]:
            student_row += [row[5], row[3], row[7], row[9]]

        overall = result_array[-1]

        match = re.search(r'\d+\.\d+|\d+', overall[2])
        scpa = extract_scpa(match)

        student_row += [scpa, overall[3], overall[5]]

        data.append(student_row)

    header = []
    for row in result_array[:-1]:
        header += [row[0] + ' ISA', row[0] + ' ESA', row[0] + ' Total', row[0] + ' Grade']
    header = ['PRN', 'Name'] + header + ['SCPA', 'Total Mark', 'Grade']

    data.insert(0, header)

    return data
