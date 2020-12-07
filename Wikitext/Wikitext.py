import re

from bs4 import BeautifulSoup, Tag, NavigableString
from pywikibot import NoPage, OtherPageSaveError

from ARQMathCode.post_reader_record import DataReaderRecord


class Wikitext:
    w_link = re.compile(r'http://en\.wikipedia\.org/wiki/(.*)')
    w= None
    highlight = []

    @staticmethod
    def data_reader():
        return DataReaderRecord('/data')

    def process_tag(self, tag: Tag):
        if tag.has_attr('class') and 'math-container' in tag['class']:
            fid = tag['id']  #
            display = ''
            highlight = fid in self.highlight
            if tag.text.startswith('$$') and not highlight:
                display = ' display=block'
            formula = tag.text.strip('$ ')
            qid = ''
            if self.w:
                try:
                    qid = f' qid={self.w.add_formula(fid, formula)}'
                except NoPage as e:
                    print(e)
                    pass
                except OtherPageSaveError:
                    pass
            tag = f'<math id={fid}{qid}{display}>{formula}</math>'
            if highlight:
                return '{{highlight|' + tag + '}}'
            else:
                return tag
        if 'a' == tag.name:
            href = tag["href"]
            m = self.w_link.match(href)
            if m:
                return f'[[w:{m.group(1)}|{tag.text}]]'
            return f'[{href} {tag.text}]'
        out = ''
        if 'p' == tag.name:
            out = "\n\n"
        if len(list(tag.children)) == 0 and tag.string:
            return tag.string
        for child in tag.children:
            if isinstance(child, Tag):
                out += self.process_tag(child)
            if isinstance(child, NavigableString):
                out += child.string
        return out

    async def to_wikitext(self, html_str: str) -> str:
        html = BeautifulSoup(html_str, 'lxml')
        return self.process_tag(html)

    def __init__(self, w=None):
        self.w = w
