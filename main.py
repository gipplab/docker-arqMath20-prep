import csv
import logging
import pickle
from os import path
from typing import TypeVar, Callable

from bs4 import BeautifulSoup

from ARQMathCode.post_reader_record import DataReaderRecord

T = TypeVar('T')


def data_reader():
    return DataReaderRecord('/data')


def to_plain(html: str) -> str:
    return ''.join(BeautifulSoup(html, 'lxml').findAll(text=True))


def get_answer_list(dr, q):
    answers = dr.get_answers_for_question(q.post_id)
    if answers is None:
        answers = []
    return answers


def pkl_read(pkl_location, data_func: Callable[[], T], refresh=False) -> T:
    if path.exists(pkl_location) and not refresh:
        with open(pkl_location, 'rb') as f:
            return pickle.load(f)
    return pkl_write(pkl_location, data_func())


def pkl_write(pkl_location, data: T) -> T:
    with open(pkl_location, 'wb') as f:
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    return data


def save_tag_subset(self: DataReaderRecord, tag):
    for question_id in list(self.post_parser.map_questions):
        question = self.post_parser.map_questions[question_id]
        lst_tags = question.tags
        if tag not in lst_tags:
            l = get_answer_list(self, question)
            for a in l:
                self.post_parser.map_answers.pop(a.post_id, None)
                self.post_parser.map_just_answers.pop(a.post_id, None)
            self.post_parser.map_questions.pop(question_id, None)


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(level=logging.DEBUG)
    filename = '/data/qa-pair-generating-functions.csv'
    if path.exists(filename):
        logger.warning("Exiting. Output file exists already.")
        exit(1)
    csvfile = open(filename, mode='w')
    fieldnames = ['qID', 'aID', 'q', 'a', 'rel']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    logger.info("Output file created.")

    dr = pkl_read('/data/dr.pickle', data_reader)
    lst_questions = dr.get_question_of_tag("generating-functions")
    logging.info(f'{len(lst_questions)} questions for tag proof')
    for q in lst_questions:
        q_text = to_plain(q.title + '\n\n' + q.body)
        answers = get_answer_list(dr, q)
        logger.debug(f'Precessing {q.title} with {len(answers)} answers')
        for a in answers:
            writer.writerow({
                'qID': q.post_id,
                'aID': a.post_id,
                'q': q_text,
                'a': to_plain(a.body),
                'rel': q.accepted_answer_id == a.post_id
            })
        csvfile.flush()
    csvfile.close()
    save_tag_subset(dr, 'generating-functions')
    pkl_write('/data/generating-functions.pickle', dr)


if __name__ == "__main__":
    main()
