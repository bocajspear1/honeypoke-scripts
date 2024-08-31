import json
import sys
from datetime import datetime, timedelta
import os

from datetime import timezone
UTC = timezone.utc


from honeypoke_extractor import HoneyPokeExtractor
from honeypoke_extractor.detect import ScanPatternDetector
from honeypoke_extractor.enrichment.address import IPAPIEnrichment

API_KEY = os.getenv("ES_API_KEY")
ES_URL = os.getenv("ES_URL")

def main():
    detectors = [
        # DownloadDetector(),
        # PHPCommandDetector(),
        # EncodedCommandDetector(),
        ScanPatternDetector(brute_force=40),
    ]

    enrichments = [
        IPAPIEnrichment()
    ]

    extractor = HoneyPokeExtractor(ES_URL, api_key=API_KEY)


    items, detector_data = extractor.get_hits(detectors=detectors,
                                              time_start=(datetime.now(UTC) - timedelta(days=1)), time_end=(datetime.now(UTC)), count=100000)
    

    ip_set = set()

    for section in detector_data['ScanPatternDetector']:
        for section_item in detector_data['ScanPatternDetector'][section]:
            ip_addr = section_item[0]
            ip_set.add(ip_addr)

    remote_ip_data = None
    ip_api = IPAPIEnrichment()
    remote_ip_data = ip_api.bulk(list(ip_set))
    
    json.dump({
        "scans": detector_data['ScanPatternDetector'],
        "remote_ip_data": remote_ip_data
    }, sys.stdout)

main()