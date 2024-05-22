import re
import ast
import os
import regex
from datetime import datetime, timedelta

from suricataparser import parse_file

from honeypoke_extractor import HoneyPokeExtractor

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
    
    
    parsed_rules = parse_rules()

    extractor = HoneyPokeExtractor(ES_URL, api_key=API_KEY)

    items = extractor.get_hits(time_start=(datetime.now() - timedelta(days=1)), time_end=(datetime.now()), count=10000)

    print(len(items))

    matched_items = []

    for item in items:
        # print(item)
        if item['input'].strip() == "":
            continue

        matched_rules = []
        for rule in parsed_rules:
            if rule['protocol'] != item['protocol']:
                continue
            if 'port' in rule and rule['port'] != item['port']:
                continue
            matches = True
            matched_values = []
            for str_match in rule['str']:
                if str_match['value'] in item['input']:
                    if str_match['do_match']:
                        matches = matches and True
                        matched_values.append(str_match['value'])
                    else:
                        matches = matches and False
                else:
                    matches = matches and False

            if len(matched_values) == 0:
                matches = False
            
            if matches:
                matched_rules.append(rule['message'])

        if len(matched_rules) > 0:
            item['matched_rules'] = matched_rules
            matched_items.append(item)

    for item in matched_items:
        print(f"\n{item['remote_ip']} - {item['protocol']}/{item['port']}")
        for rule in item['matched_rules']:
            print(f"  - {rule}")
main()



