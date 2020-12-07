import csv
import logging
import pickle
from os import path
from typing import TypeVar, Callable, Dict, List

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
    logger = logging.getLogger(__name__)
    logger.debug('map sizes %s %s', len(self.post_parser.map_questions), len(self.post_parser.map_answers))
    user_whitelist = {}
    duplicate_whitelist = {}
    related_whitelist = {}
    keep_questions = self.get_question_of_tag(tag)
    keep_qid = []

    def add_user(uid):
        if uid is None:
            user_whitelist[-1] = self.user_parser.map_of_user[-1]
        else:
            current_user = self.user_parser.map_of_user.get(uid)
            if current_user:
                user_whitelist[uid] = current_user
            else:
                logger.warning(f'user {uid} not mapped')

    def add_users(quest_id):
        for c in self.comment_parser.map_of_comments_for_post.get(quest_id, []):
            add_user(c.user_id)
        for v in self.vote_parser.map_of_votes.get(quest_id, []):
            add_user(v.user_id)
        for answer in answers:
            add_user(answer.owner_user_id)
            add_user(answer.last_editor_user_id)
            for c in self.comment_parser.map_of_comments_for_post.get(answer.post_id, []):
                add_user(c.user_id)
            for v in self.vote_parser.map_of_votes.get(answer.post_id, []):
                add_user(v.user_id)

    def insert_related(d: Dict[str, List[str]], k, l: List, wl: Dict):
        if d.get(k):
            keep_qid.extend(d.get(k))
            wl[k] = d.get(k)
        for key, value in d.items():
            if k in value:
                keep_qid.extend(value)
                wl[key] = d.get(key)

    for question in list(keep_questions):
        keep_qid.append(question.post_id)
        insert_related(self.post_link_parser.map_duplicate_posts, question.post_id, keep_questions, duplicate_whitelist)
        insert_related(self.post_link_parser.map_related_posts, question.post_id, keep_questions, related_whitelist)
    self.post_link_parser.map_related_posts = related_whitelist
    self.post_link_parser.map_duplicate_posts = duplicate_whitelist

    for question_id in list(self.post_parser.map_questions):
        question = self.post_parser.map_questions[question_id]
        answers = get_answer_list(self, question)
        if question_id not in keep_qid:
            for a in answers:
                self.post_parser.map_just_answers.pop(a.post_id, None)
                self.comment_parser.map_of_comments_for_post.pop(a.post_id, None)
                self.vote_parser.map_of_votes.pop(a.post_id, None)
            self.post_parser.map_answers.pop(question_id, None)
            self.post_parser.map_questions.pop(question_id, None)
            self.comment_parser.map_of_comments_for_post.pop(question_id, None)
            self.vote_parser.map_of_votes.pop(question_id, None)
            logger.debug('map sizes %s %s', len(self.post_parser.map_questions),
                         len(self.comment_parser.map_of_comments_for_post))
        else:
            add_users(question_id)

    self.user_parser.map_of_user = user_whitelist


def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    logger.setLevel(level=logging.DEBUG)
    filename = '/data/qonly.csv'
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
