import requests
from bs4 import BeautifulSoup


def get_semester_wise_exam_metadata(exam_options, semesters):
    """Get semester wise exam metadata"""
    semester_wise_array = {}
    for option in exam_options:
        exam_name = option.get_text(strip=True)
        exam_value = option["value"].strip()

        for sem in semesters:
            if sem in exam_name.upper():
                if sem not in semester_wise_array:
                    semester_wise_array[sem] = []
                else:
                    semester_wise_array[sem].append(
                        {"exam_name": exam_name.upper(), "exam_id": exam_value}
                    )

    return semester_wise_array


def get_exam_metadata(url, semesters):
    """Get exam name and its id"""
    html = requests.get(url).content
    soup = BeautifulSoup(html, "html.parser")

    exam_options = soup.select("#exam_id option[value]")[1:]

    semeseter_wise_exam_metadata = get_semester_wise_exam_metadata(exam_options, semesters)
    
    for sem in semeseter_wise_exam_metadata:
        semeseter_wise_exam_metadata[sem].sort(  
            key=lambda x: int(x["exam_name"].split()[-1]),
            reverse=True,
        )
        
    return semeseter_wise_exam_metadata
