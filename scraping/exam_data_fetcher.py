from scrapy import Selector
import requests

def get_exam_names_and_ids(category):
    try:
        semesters = ["FIRST SEMESTER", "SECOND SEMESTER", "THIRD SEMESTER",
                     "FOURTH SEMESTER"]
        if category == "PG":
           url = "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/PGResultViewSec_ctrl/" 
        else:
            url = "https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/"
            semesters = semesters + ["FIFTH SEMESTER", "SIXTH SEMESTER"]

        html = requests.get(url).content
        sel = Selector(text=html)

        options = sel.xpath('//*[@id="exam_id"]/option')[1:]

        semester_array = []

        # Helper function to extract the year from the exam name
        def get_year(exam_name):
            return int(exam_name.split()[-1])

        for sem in semesters:
            semester_dict = {}
            for option in options:
                key = option.xpath('text()').get().strip()
                value = option.xpath('@value').get().strip()

                if sem in key:
                    semester_dict[key.replace(sem+" ", "")] = value

            # Sort the exam names within each semester based on the year
            sorted_exams = sorted(semester_dict.items(), key=lambda x: get_year(x[0]), reverse=True)
            semester_array.append(dict(sorted_exams))

        return semester_array

    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return []
