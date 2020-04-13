import logging
import re
from os import getenv
from typing import Optional

import pywikibot
import pywikibot.flow
from bs4 import BeautifulSoup, Tag, NavigableString
from signal import *

from pywikibot import Claim

from main import get_answer_list, pkl_read, pkl_write
from ARQMathCode.post_reader_record import DataReaderRecord


def data_reader():
    return DataReaderRecord('/data')


data_repo = None
w_link = re.compile(r'http://en\.wikipedia\.org/wiki/(.*)')
qid = {
    'users': {},
    'posts': {},
    'formulae': {},
}


def get_formula(fid) -> Optional[str]:
    global qid
    return qid['formulae'].get(fid)


def add_formula(fid):
    global qid
    if get_formula(fid):
        return pywikibot.ItemPage(get_data_repo(), get_formula(fid))
    new_item = pywikibot.ItemPage(get_data_repo())
    new_item.editLabels(labels={"en": f"Formula {fid}"})
    p8 = pywikibot.Claim(get_data_repo(), u'P8')
    p8.setTarget(fid)
    new_item.addClaim(p8)
    new_id = new_item.getID()
    qid['formulae'][fid] = new_id
    return new_item


def get_data_repo():
    global data_repo
    if not data_repo:
        site = get_site()
        data_repo = site.data_repository()
    return data_repo


site = None


def get_site():
    global site
    if not site:
        site = pywikibot.Site('fse', 'fse')  # The site we want to run our bot on
        if getenv('WIKI_PASS'):
            patch_wiki()
        site.login()
    return site


def process_tag(tag: Tag):
    global w_link
    if tag.has_attr('class') and 'math-container' in tag['class']:
        fid = tag['id']
        formula = tag.text
        new_item = add_formula(fid)
        new_item.get()
        if 'P1' in new_item.claims:
            claim: Claim = new_item.claims['P1'][0]
            if claim.target != formula:
                claim.changeTarget(formula)
        else:
            p1 = pywikibot.Claim(get_data_repo(), u'P1')
            p1.setTarget(formula)
            new_item.addClaim(p1)
        return f'<math id={fid} qid={get_formula(fid)}>{formula}</math>'
    if 'a' == tag.name:
        href = tag["href"]
        m = w_link.match(href)
        if m:
            return f'[[w:{m.group(1)}|{tag.text}]]'
        return f'[{href} {tag.text}]'
    if tag.string:
        return tag.string
    out = ''
    for child in tag.children:
        if isinstance(child, Tag):
            out += process_tag(child)
        if isinstance(child, NavigableString):
            out += child.string
    return out


def to_wikitext(html_str: str) -> str:
    html = BeautifulSoup(html_str, 'lxml')
    return process_tag(html)


# def testbot():
#     new_item = pywikibot.ItemPage(drepo)
#     board = pywikibot.flow.Board(site, "pwTest")
#     title = 'New topic'
#     content = 'This is a new topic.'
#     topic = board.new_topic(title, content)
#     new_item.editLabels(labels={"en": "Hamburg Main Station", "de": "Hamburg Hauptbahnhof"})
#     print(new_item.getID())


# TODO: https://www.mediawiki.org/wiki/Manual:Pywikibot/OAuth
def patch_wiki():
    import pywikibot

    original = pywikibot.input

    def new_input(question, password=False, default='', force=False):
        if password:
            return getenv('WIKI_PASS')
        return original(question, password, default, force)

    pywikibot.input = new_input


def load_qid():
    global qid
    qid = pkl_read('/data/qid.pickle', lambda: qid)


def save_qid():
    global qid
    pkl_write('/data/qid.pickle', qid)


def add_topic(q):
    q_text = to_wikitext(q.title + '\n\n' + q.body)
    pass


def add_answer(a):
    a_text = to_wikitext(a.body)
    pass


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(level=logging.DEBUG)
    for sig in (SIGABRT, SIGILL, SIGINT, SIGSEGV, SIGTERM):
        signal(sig, save_qid)
    load_qid()
    dr = pkl_read('/data/dr.pickle', data_reader)
    lst_questions = dr.get_question_of_tag("proof-writing")
    logging.info(f'{len(lst_questions)} questions for tag calculus')
    # for questionId, q in dr.post_parser.map_questions.items():
    for q in lst_questions:
        answers = get_answer_list(dr, q)
        logger.debug(f'Precessing {q.title} with {len(answers)} answers')
        add_topic(q)
        for a in answers:
            add_answer(a)
        save_qid()


if __name__ == "__main__":
    main()
