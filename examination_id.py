from scrapy import Selector
import requests

url = 'https://dsdc.mgu.ac.in/exQpMgmt/index.php/public/ResultView_ctrl/'

def findId():
    html = requests.get(url).content
    sel = Selector(text=html)

    options = sel.xpath('//*[@id="exam_id"]/option')[1:] # don't want the Select Examination option

    options_dict = {}

    for option in options:
        key = option.xpath('text()').get().strip()
        value = option.xpath('@value').get().strip()
        options_dict[key] = value 

    return options_dict
