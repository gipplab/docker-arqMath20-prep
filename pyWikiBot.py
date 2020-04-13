import csv
import logging
from os import getenv

import pywikibot
import pywikibot.flow
import re
from bs4 import BeautifulSoup, Tag, NavigableString

from ARQMathCode.post_reader_record import DataReaderRecord

data_repo = None
w_link = re.compile(r'http://en\.wikipedia\.org/wiki/(.*)')


def get_data_repo():
    global data_repo
    if not data_repo:
        site = pywikibot.Site('fse', 'fse')  # The site we want to run our bot on
        if getenv('WIKI_PASS'):
            patch_wiki()
        site.login()
        data_repo = site.data_repository()
    return data_repo


def process_tag(tag: Tag):
    global w_link
    if tag.has_attr('class') and 'math-container' in tag['class']:
        fid = tag['id']
        formula = tag.text
        # qid = 0
        new_item = pywikibot.ItemPage(get_data_repo())
        qid = new_item.get()
        p1 = pywikibot.Claim(get_data_repo(), u'P1')
        p1.setTarget(formula)
        new_item.addClaim(p1)
        p8 = pywikibot.Claim(get_data_repo(), u'P8')
        p8.setTarget(fid)
        return f'<math id={fid} qid={qid}>{formula}</math>'
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


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(level=logging.DEBUG)
    # chmod('/app/user-config.py', 0o600)
    # patch_wiki()
    # testbot()
    # exit(0)
    # if path.exists('/data/qa-pair.csv'):
    #     logger.warning("Exiting. Output file exists already.")
    #     exit(1)
    csvfile = open('/data/qa-pair.csv', mode='w')
    fieldnames = ['qID', 'aID', 'q', 'a', 'rel']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    logger.info("Output file created.")
    dr = DataReaderRecord('/data')
    lst_questions = dr.get_question_of_tag("proof-writing")
    logging.info(f'{len(lst_questions)} questions for tag calculus')
    # for questionId, q in dr.post_parser.map_questions.items():
    for q in lst_questions:
        q_text = to_wikitext(q.title + '\n\n' + q.body)
        answers = get_answer_list(dr, q)
        logger.debug(f'Precessing {q.title} with {len(answers)} answers')
        for a in answers:
            writer.writerow({
                'qID': q.post_id,
                'aID': a.post_id,
                'q': q_text,
                'a': to_wikitext(a.body),
                'rel': q.accepted_answer_id == a.post_id
            })
        csvfile.flush()
    csvfile.close()


def get_answer_list(dr, q):
    answers = dr.get_answers_for_question(q.post_id)
    if answers is None:
        answers = []
    return answers


if __name__ == "__main__":
    main()
