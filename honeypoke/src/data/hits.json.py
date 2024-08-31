import json
import sys
import os
from datetime import datetime, UTC, timedelta

from honeypoke_extractor import HoneyPokeExtractor
from honeypoke_extractor.detect import DownloadDetector, PHPCommandDetector, EncodedCommandDetector, EmergingThreatRules
from honeypoke_extractor.enrichment.address import IPAPIEnrichment

API_KEY = os.getenv("ES_API_KEY")
ES_URL = os.getenv("ES_URL")

def main():
    detectors = [
        # DownloadDetector(),
        # PHPCommandDetector(),
        # EncodedCommandDetector(),
        # ScanPatternDetector(),
        EmergingThreatRules(),
    ]

    enrichments = [
        IPAPIEnrichment()
    ]

    extractor = HoneyPokeExtractor(ES_URL, api_key=API_KEY)


    items, detector_data = extractor.get_hits(detectors=detectors, bulk_ip_enrichments=enrichments,
                                              time_start=(datetime.now(UTC) - timedelta(days=1)), time_end=(datetime.now(UTC)), count=100000, return_matches=True)
    
    remote_ips = {}
    remote_ip_data = detector_data['IPAPIEnrichment']
    matched_items = items

    for match_item in matched_items:
        remote_ip = match_item['remote_ip']
        port_data = f"{match_item['protocol']}/{match_item['port']}"
        if remote_ip not in remote_ips:
            remote_ips[remote_ip] = {}
        
        if port_data not in remote_ips[remote_ip]:
            remote_ips[remote_ip][port_data] = {}

        # if remote_ip not in remote_ip_data:
        #     remote_ip_data[remote_ip] = match_item['ipapi']

        for matched_rule_data in match_item['matched_rules']:
            matched_rule = matched_rule_data[0]
            if not matched_rule in remote_ips[remote_ip][port_data]:
                remote_ips[remote_ip][port_data][matched_rule] = 0
            remote_ips[remote_ip][port_data][matched_rule] += 1
    
    json.dump({
        "rules": detector_data['EmergingThreatRules']['rules'],
        "remote_ips": remote_ips,
        "remote_ip_data": remote_ip_data
    }, sys.stdout)

main()