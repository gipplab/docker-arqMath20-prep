from ARQMathCode.post_reader_record import DataReaderRecord
import csv

csvfile = open('/data/qa-pair.csv', mode='w')
fieldnames = ['qId', 'aID', 'q', 'a', 'rel']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()


def main():
    dr = DataReaderRecord('/data')
    lst_questions = dr.get_question_of_tag("calculus")
    for q in lst_questions:
        for a in dr.get_answers_for_question(q):
            writer.writerow({
                'qID': q.post_id,
                'aID': a.post_id,
                'q': q.to_str(),
                'a': a.to_str(),
                'rel': q.accepted_answer_id == a.post_id
            })


if __name__ == "__main__":
    main()
