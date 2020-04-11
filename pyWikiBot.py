import logging
from os import path
import csv

from bs4 import BeautifulSoup, Tag, NavigableString
from lxml.html.soupparser import fromstring
from ARQMathCode.post_reader_record import DataReaderRecord


def process_tag(tag: Tag):
    if tag.has_attr('class') and 'math-container' in tag['class']:
        return f'<math id={tag["id"]}>{tag.text}</math>'
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


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(level=logging.DEBUG)
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
