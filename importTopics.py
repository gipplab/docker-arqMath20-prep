import asyncio

import pywikibot.flow

from Topics.TopicReader import TopicReader
from Wikidata.Wikidata import Wikidata
from Wikitext.Wikitext import Wikitext

formula_reader = TopicReader('/data/Topics_V1.1.xml')
text_reader = TopicReader('/data/Topics_V2.0.xml')
wd = Wikidata()

tasks = []

board = pywikibot.flow.Board(wd.get_site(), "Formula Topics")


async def addTopic(tid, text, wt):
    wt = await wt.to_wikitext(text)
    id_title= f'Topic {tid}'
    for t in board.topics():
        post: pywikibot.flow.Post = t.root
        if id_title == post.get('topic-title-wikitext'):
            raise NotImplementedError("PyWikiBot cannot change topics")
    board.new_topic(id_title, wt)


for k, v in formula_reader.map_topics.items():
    wt = Wikitext(wd)
    wt.highlight = [v.formula]
    text = f"== {v.title} == \n\n{v.question}"
    t = addTopic(k, text, wt)
    tasks.append(t)


async def run():
    await asyncio.gather(*tasks)


asyncio.run(run())
