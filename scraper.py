from scrapy import Selector
import requests
import re

url = 'https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/'

def scrape(exam_id, start_prn, end_prn):
    data = []
    for prn in range(start_prn, end_prn + 1):
        payload = {'exam_id': str(exam_id), 'prn': str(prn), 'btnresult': 'Get Result'}

        html = requests.post(url, data=payload).content
        sel = Selector(text=html)

        garbage_rows = sel.xpath('//*[@class="frame"]').xpath('./table[2]//tr')

        i = -1
        for row_selector in garbage_rows:
            i = i + 1
            height_attribute = row_selector.xpath('@height').extract_first()
            if height_attribute == '30':
                break

        mark_rows = garbage_rows[2:i + 1]

        result_array = []

        for row in mark_rows:
            inner_array = []
            for td_element in row.xpath('.//td'):
                inner_array.append(td_element.xpath('normalize-space()').extract_first())
            result_array.append(inner_array)

        current_prn = sel.xpath('//*[@id="prn"]/@value').extract_first()
        name = sel.xpath('//*[@style="font-size:14px;color:#936;"]/text()').extract_first()
        if (not name):
            continue

        student_row = [current_prn, name]

        for row in result_array[:-1]:
            student_row = student_row + [row[5], row[3], str(int(row[3]) + int(row[5])), row[9] if row[9] != '---' else 'Fail']

        overall = result_array[-1]

        match = re.search(r'\d+\.\d+|\d+', overall[2])
        if match:
            scpa = str(float(match.group()))
        else:
            scpa = 'Fail'

        student_row = student_row + [scpa, overall[3] if overall[3] != '---' else 'Fail', overall[5] if overall[5] != '---' else 'Fail']

        data.append(student_row)

    header = []
    for row in result_array[:-1]:
        header = header + [row[0] + ' ISA', row[0] + ' ESA', row[0] + ' Total', row[0] + ' Grade']
    header = ['PRN', 'Name'] + header + ['SCPA', 'Total Mark', 'Grade']

    data.insert(0, header)
    
    return data
