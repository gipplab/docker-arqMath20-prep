import asyncio
import csv

from Topics.TopicReader import TopicReader
from Wikitext.Wikitext import Wikitext

formula_reader = TopicReader('C:/git/fairmat/docker-arqMath20-prep/test/data/Topics_V1.1.xml')
text_reader = TopicReader('C:/git/fairmat/docker-arqMath20-prep/test/data/Topics_V2.0.xml')

tasks = []

filename = 'C:/git/fairmat/docker-arqMath20-prep/test/data/topic-text.csv'
csvfile = open(filename, mode='w',encoding='utf-8')
fieldnames = ['tid','text']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()



async def addTopic(tid, v, wt):
    text = f"== {v.title} == \n\n{v.question}"
    wikitext = await wt.to_wikitext(text)
    writer.writerow({
        'tid': tid,
        'text': wikitext.strip()
    })

for k, v in formula_reader.map_topics.items():
    wt = Wikitext()
    wt.highlight = [v.formula]
    t = addTopic(k, v, wt)
    tasks.append(t)

for k, v in text_reader.map_topics.items():
    wt = Wikitext()
    wt.highlight = [v.formula]
    t = addTopic(k, v, wt)
    tasks.append(t)


async def run():
    await asyncio.gather(*tasks)


asyncio.run(run())
