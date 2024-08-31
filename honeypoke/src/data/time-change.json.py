from pprint import pprint
import os
import sys
import json

from datetime import timedelta, datetime

from datetime import timezone
UTC = timezone.utc


from honeypoke_extractor import HoneyPokeExtractor


API_KEY = os.getenv("ES_API_KEY")
ES_URL = os.getenv("ES_URL")

def main():
    
    extractor = HoneyPokeExtractor(ES_URL, api_key=API_KEY)

    today_list = extractor.get_top_ports(count=30)
    yesterday_list = extractor.get_top_ports(count=30, time_start=(datetime.now(UTC) - timedelta(hours=48)), time_end=(datetime.now(UTC) - timedelta(hours=24)))
    last_week_list = extractor.get_top_ports(count=30, time_start=(datetime.now(UTC) - timedelta(days=7)), time_end=(datetime.now(UTC) - timedelta(hours=24)))

    day_change_list = []

    # Get today's percentages
    day_total = 0
    for item in today_list:
        day_total += item['count']

    for i in range(len(today_list)):
        today_list[i]['percent'] = (today_list[i]['count'] / day_total) * 100

    # Get yesterday's percentages
    yesterday_total = 0
    for item in yesterday_list:
        yesterday_total += item['count']

    for i in range(len(yesterday_list)):
        yesterday_list[i]['percent'] = (yesterday_list[i]['count'] / yesterday_total) * 100

    # Get week's percentages
    week_total = 0
    for item in last_week_list:
        week_total += item['count']

    for i in range(len(last_week_list)):
        last_week_list[i]['percent'] = (last_week_list[i]['count'] / week_total) * 100

    day_differences = []
    week_differences = []


    for item in today_list:
        day_percent_diff = 0
        week_percent_diff = 0

        yesterday_count = 0
        yesterday_percent = 0
        week_count_percent = 0

        for check_item in yesterday_list:
            if item['protocol'] == check_item['protocol'] and item['port'] == check_item['port']:
                day_percent_change = item['percent'] - check_item['percent']
                day_percent_diff = (day_percent_change / check_item['percent']) * 100
                yesterday_count = check_item['count']
                yesterday_percent = check_item['percent']

        for check_item in last_week_list:
            if item['protocol'] == check_item['protocol'] and item['port'] == check_item['port']:
                week_percent_change = item['percent'] - check_item['percent']
                week_percent_diff = (week_percent_change / check_item['percent']) * 100
                week_count_percent = check_item['percent']
        
        if yesterday_count == 0:
            day_percent_diff = item['percent']

        if week_count_percent == 0:
            week_percent_diff = item['percent']

        # print(f"{item['protocol']}/{item['port']} = {day_percent_diff} ({week_percent_diff})")
        if abs(day_percent_diff) >= 30.0:
            day_differences.append({
                "port": f"{item['protocol']}/{item['port']}",
                "percent_change": day_percent_diff,
                "yesterday_percent": yesterday_percent,
                "today_percent": item['percent']
            })
            # print(f" -  > 2.0, today = {item['count']}, yesterday = {yesterday_count}")

        if abs(week_percent_diff) >= 30.0:
            week_differences.append({
                "port": f"{item['protocol']}/{item['port']}",
                "percent_change": week_percent_diff,
                "week_percent": week_count_percent,
                "today_percent": item['percent']
            })
            # print(f" - {item['protocol']}/{item['port']} >= 3.0, today = {item['percent']}%, last_week = {week_count_percent}%")
    

    json.dump({
        "week_differences": week_differences,
        "day_differences": day_differences
    }, sys.stdout)
    
main()
