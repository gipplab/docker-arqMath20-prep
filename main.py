import csv
import logging

from ARQMathCode.post_reader_record import DataReaderRecord

root = logging.getLogger()
root.setLevel(logging.DEBUG)


csvfile = open('/data/qa-pair.csv', mode='w')
fieldnames = ['qId', 'aID', 'q', 'a', 'rel']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()
logging.info("Output file created.")


def main():
    dr = DataReaderRecord('/data')
    lst_questions = dr.get_question_of_tag("calculus")
    logging.info(f'{len(lst_questions)} questions for tag calculus')
    for q in lst_questions:
        q_text = q.to_str()
        answers = dr.get_answers_for_question(q)
        logging.debug(f'Precessing {q.title} with {len(answers)} answers')
        for a in answers:
            writer.writerow({
                'qID': q.post_id,
                'aID': a.post_id,
                'q': q_text,
                'a': a.to_str(),
                'rel': q.accepted_answer_id == a.post_id
            })


if __name__ == "__main__":
    main()
