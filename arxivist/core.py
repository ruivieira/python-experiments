"""Library to fetch pre-prints from arXiv"""
# INFO: Library to fetch pre-prints from arXiv
# pylint: disable=no-self-use
from urllib.parse import urlencode
import urllib.request
import xml.etree.ElementTree as ET
from typing import Dict, List

BASE_URL = "http://export.arxiv.org/oai2"
NAMESPACE = "{http://www.openarchives.org/OAI/2.0/}"
ARXIV_NS = "{http://arxiv.org/OAI/arXiv/}"


class Entry:
    """Represents an arXiv entry"""

    def __init__(self):
        self.arxiv_id = None
        self.title = None

    def __str__(self) -> str:
        return f"[id: {self.arxiv_id}, title: {self.title}]"

    def __repr__(self) -> str:
        return self.__str__()


class ArXivist:
    """Fetches data from arXiv"""

    def __init__(self):
        self.params: Dict[str, str] = {}
        self.params["verb"] = "ListRecords"
        self.params["metadataPrefix"] = "arXiv"
        self.params["set"] = "stat"

    def parse_element(self, element) -> Entry:
        """Parse a metadata element"""
        # print(record)
        entry = Entry()
        metadata = element.find(f"{NAMESPACE}metadata").find(f"{ARXIV_NS}arXiv")
        entry.arxiv_id = metadata.find(f"{ARXIV_NS}id").text
        entry.title = metadata.find(f"{ARXIV_NS}title").text
        return entry

    def fetch(self, start: str, end: str) -> List[Entry]:
        """Get papers between start and end date"""
        self.params["from"] = start
        self.params["until"] = end

        param_str = urlencode(self.params)

        # print(param_str)

        with urllib.request.urlopen(f"{BASE_URL}?{param_str}") as response:
            xml = response.read()

        root = ET.fromstring(xml)
        # print(root)

        entries: List[Entry] = []

        records = root.findall(NAMESPACE + "ListRecords/" + NAMESPACE + "record")

        for record in records:
            entry = self.parse_element(record)
            entries.append(entry)

        return entries
