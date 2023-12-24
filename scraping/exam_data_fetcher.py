from scrapy import Selector
import requests

def get_exam_names_and_ids(url):
    try:
        html = requests.get(url).content
        sel = Selector(text=html)

        options = sel.xpath('//*[@id="exam_id"]/option')[1:]

        options_dict = {}

        for option in options:
            key = option.xpath('text()').get().strip()
            value = option.xpath('@value').get().strip()
            options_dict[key] = value

        return options_dict

    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return {}
