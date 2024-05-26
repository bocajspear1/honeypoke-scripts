from pprint import pprint
import os
import sys
from datetime import timedelta, datetime, date

from honeypoke_extractor import HoneyPokeExtractor

from jinja2 import Environment, FileSystemLoader, select_autoescape

API_KEY = os.getenv("ES_API_KEY")
ES_URL = os.getenv("ES_URL")

def main():
        
    output_file = "./time-compare.html"
    if len(sys.argv) == 2:
        output_file = sys.argv[1]

    jinja_env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape()
    )
    
    extractor = HoneyPokeExtractor(ES_URL, api_key=API_KEY)

    

    today_list = extractor.get_top_ports(count=20)

    top_labels = []
    top_values = []

    yesterday_list = extractor.get_top_ports(count=20, time_start=(datetime.now() - timedelta(hours=48)), time_end=(datetime.now() - timedelta(hours=24)))
    last_week_list = extractor.get_top_ports(count=20, time_start=(datetime.now() - timedelta(days=7)), time_end=(datetime.now() - timedelta(hours=24)))

    today_total = 0
    for item in today_list:
        today_total += item['count']
        if len(top_labels) <= 10:
            top_labels.append(f"{item["protocol"]}/{item["port"]}")
            top_values.append(item['count'])
    # print(f"today total = {today_total}")

    for i in range(len(today_list)):
        today_list[i]['percent'] = (today_list[i]['count'] / today_total) * 100

    yesterday_total = 0
    for item in yesterday_list:
        yesterday_total += item['count']

    for i in range(len(yesterday_list)):
        yesterday_list[i]['percent'] = (yesterday_list[i]['count'] / yesterday_total) * 100

    # print(f"yesterday total = {yesterday_total}")

    week_total = 0
    for item in last_week_list:
        week_total += item['count']

    for i in range(len(last_week_list)):
        last_week_list[i]['percent'] = (last_week_list[i]['count'] / week_total) * 100

    day_columns = []
    day_values = []

    week_columns = []
    week_values = []

    for item in today_list:
        day_percent_diff = 0
        week_percent_diff = 0
        yesterday_count = 0
        week_count_percent = 0
        for check_item in yesterday_list:
            if item['protocol'] == check_item['protocol'] and item['port'] == check_item['port']:
                day_percent_diff = item['percent'] - check_item['percent']
                yesterday_count = check_item['count']

        for check_item in last_week_list:
            if item['protocol'] == check_item['protocol'] and item['port'] == check_item['port']:
                week_percent_diff = item['percent'] - check_item['percent']
                week_count_percent = check_item['percent']
        
        if yesterday_count == 0:
            day_percent_diff = item['percent']

        if week_count_percent == 0:
            week_percent_diff = item['percent']

        # print(f"{item['protocol']}/{item['port']} = {day_percent_diff} ({week_percent_diff})")
        if abs(day_percent_diff) >= 2.0:
            day_columns.append(f"{item["protocol"]}/{item["port"]}")
            day_values.append(day_percent_diff)
            # print(f" -  > 2.0, today = {item['count']}, yesterday = {yesterday_count}")

        if abs(week_percent_diff) >= 3.0:
            week_columns.append(f"{item["protocol"]}/{item["port"]}")
            week_values.append(week_percent_diff)
            # print(f" - {item['protocol']}/{item['port']} >= 3.0, today = {item['percent']}%, last_week = {week_count_percent}%")

    
    time_compare_template = jinja_env.get_template("time-compare.html")
    page_output = time_compare_template.render(
        top_insert_labels=top_labels, top_insert_values=top_values,
        x_day_insert_data=day_columns, y_day_insert_data=day_values,
        x_week_insert_data=week_columns, y_week_insert_data=week_values,
        today=date.today().isoformat()
    )

    with open(output_file, "w") as out:
        out.write(page_output)
main()
