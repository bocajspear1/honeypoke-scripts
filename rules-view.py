import re
import ast
import os
import regex
import sys
from datetime import datetime, timedelta, date

from suricataparser import parse_file

from honeypoke_extractor import HoneyPokeExtractor

from jinja2 import Environment, FileSystemLoader, select_autoescape

API_KEY = os.getenv("ES_API_KEY")
ES_URL = os.getenv("ES_URL")

def parse_rules():
    parsed_rules = []
    rule_dir = "./rules"
    rules_dir_list = os.listdir(rule_dir)
    for dir_item in rules_dir_list:
        if dir_item.endswith(".rules"):
            rule_path = os.path.join(rule_dir, dir_item)
            raw_rules = parse_file(rule_path)
            for rule in raw_rules:
                if not rule.enabled:
                    continue

                header_split_1 = rule.header.split("->")
                source_split = header_split_1[0].strip().split(" ")
                dest_split = header_split_1[1].strip().split(" ")
                
                new_rule = {
                    "str": [],
                    "regex": [],
                    "protocol": source_split[0],
                }

                if dest_split[1].isnumeric():
                    new_rule['port'] = int(dest_split[1])
                
                wrong_direction = False
                for option in rule.options:
                    if option.name == "content":
                        content_str = option.value
                        matches = re.findall(r'\|(?:[0-9a-fA-F]{2}[ |])+', content_str)
                        for match in matches:
                            hexified = "\\x" + match[1:-1].replace(" ", "\\x")
                            content_str = content_str.replace(match, hexified)
                        

                        do_match = True
                        if content_str.startswith("!"):
                            content_str = content_str[1:]
                            do_match = False

                        content_str = content_str.replace("\\:", ":")
                        content_str = content_str.replace("\\;", ";")
                        
                        new_rule['str'].append({
                            "value": ast.literal_eval(content_str),
                            "do_match": do_match
                        })
                    elif option.name == "msg":
                        new_rule['message'] = option.value[1:-1]
                    elif option.name == "flow":
                        if "from_server" in option.value:
                            wrong_direction = True
                    elif option.name == "pcre":
                        re_flags = 0
                        re_value = option.value[1:-1]
                        if re_value.startswith("/"):
                            re_value = re_value[1:]
                            while not re_value.endswith("/"):
                                if re_value[-1] == "i":
                                    re_flags |= regex.IGNORECASE
                                re_value = re_value[:-1]
                            re_value = re_value[:-1]
                        # print(option.value, re_value)
                        new_rule['regex'].append({
                            "value": regex.compile(re_value)
                        })
                    else:
                        # print(option)
                        pass
                # print(new_rule)
                if not wrong_direction:
                    parsed_rules.append(new_rule)
    return parsed_rules

def main():
    
    output_file = "./rules-view.html"
    if len(sys.argv) == 2:
        output_file = sys.argv[1]

    jinja_env = Environment(
        loader=FileSystemLoader("templates"),
        autoescape=select_autoescape()
    )
    
    parsed_rules = parse_rules()

    extractor = HoneyPokeExtractor(ES_URL, api_key=API_KEY)

    hit_items = extractor.get_hits(time_start=(datetime.now() - timedelta(days=1)), time_end=(datetime.now()), count=10000)

    print(len(hit_items))

    port_map = {}
    rules_map = {}
    matched_items = []

    for hit_item in hit_items:
        # print(item)
        if hit_item['input'].strip() == "":
            continue

        port_data = f"{hit_item['protocol']}/{hit_item['port']}"

        matched_rules = []
        for rule in parsed_rules:
            if rule['protocol'] != hit_item['protocol']:
                continue
            if 'port' in rule and rule['port'] != hit_item['port']:
                continue

            matches_all = True
            matched_values = []
            for str_match in rule['str']:
                if str_match['value'] in hit_item['input']:
                    if str_match['do_match']:
                        matches_all = matches_all and True
                        matched_values.append(str_match['value'])
                    else:
                        matches_all = matches_all and False
                else:
                    matches_all = matches_all and False

            if matches_all and 'regex' in rule and len(rule['regex']) > 0:
                for regex_match in rule['regex']:
                    if regex_match['value'].search(hit_item['input']):
                        matches_all = matches_all and True
                    else:
                        matches_all = matches_all and False

            if len(matched_values) == 0:
                matches_all = False
            
            if matches_all:
                matched_rules.append(rule['message'])
                if rule['message'] not in rules_map:
                    rules_map[rule['message']] = 0
                rules_map[rule['message']] += 1

        if len(matched_rules) > 0:
            hit_item['matched_rules'] = matched_rules
            matched_items.append(hit_item)
            if port_data not in port_map:
                port_map[port_data] = 0
            port_map[port_data] += 1

    match_labels = []
    match_values = []
    for rule in rules_map:
        match_labels.append(rule)
        match_values.append(rules_map[rule])

    port_labels = []
    port_values = []
    for port_data in port_map:
        port_labels.append(port_data)
        port_values.append(port_map[port_data])

    filtered_matches = {}
    for match_item in matched_items:
        remote_ip = match_item['remote_ip']
        port_data = f"{match_item['protocol']}/{match_item['port']}"
        if remote_ip not in filtered_matches:
            filtered_matches[remote_ip] = {}
        
        if port_data not in filtered_matches[remote_ip]:
            filtered_matches[remote_ip][port_data] = {}

        for matched_rule in match_item['matched_rules']:
            if not matched_rule in filtered_matches[remote_ip][port_data]:
                filtered_matches[remote_ip][port_data][matched_rule] = 0
            filtered_matches[remote_ip][port_data][matched_rule] += 1


        
        



    time_compare_template = jinja_env.get_template("rules-view.html")
    page_output = time_compare_template.render(
        match_insert_labels=match_labels, match_insert_values=match_values,
        port_insert_labels=port_labels, port_insert_values=port_values,
        matches=filtered_matches,
        today=date.today().isoformat()
    )

    with open(output_file, "w") as out:
        out.write(page_output)

main()



