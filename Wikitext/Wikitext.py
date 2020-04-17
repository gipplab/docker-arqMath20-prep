import re

from bs4 import BeautifulSoup, Tag, NavigableString

from ARQMathCode.post_reader_record import DataReaderRecord
from Wikidata import Wikidata


class Wikitext:
    w_link = re.compile(r'http://en\.wikipedia\.org/wiki/(.*)')
    w: Wikidata = None

    @staticmethod
    def data_reader():
        return DataReaderRecord('/data')

    def process_tag(self, tag: Tag):
        if tag.has_attr('class') and 'math-container' in tag['class']:
            fid = tag['id']
            formula = tag.text.strip('$ ')
            qid = ''
            if self.w:
                qid = f' qid={self.w.get_formula(fid, formula)}'
            return f'<math id={fid}{qid}>{formula}</math>'
        if 'a' == tag.name:
            href = tag["href"]
            m = self.w_link.match(href)
            if m:
                return f'[[w:{m.group(1)}|{tag.text}]]'
            return f'[{href} {tag.text}]'
        if tag.string:
            return tag.string
        out = ''
        for child in tag.children:
            if isinstance(child, Tag):
                out += self.process_tag(child)
            if isinstance(child, NavigableString):
                out += child.string
        return out

    def to_wikitext(self, html_str: str) -> str:
        html = BeautifulSoup(html_str, 'lxml')
        return self.process_tag(html)

    def __init__(self, w=None):
        self.w = w
