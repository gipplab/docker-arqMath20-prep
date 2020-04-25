import asyncio

import pywikibot.flow

from Topics.TopicReader import TopicReader
from Wikidata.Wikidata import Wikidata
from Wikitext.Wikitext import Wikitext

formula_reader = TopicReader('/data/Topics_V1.1.xml')
text_reader = TopicReader('/data/Topics_V2.0.xml')
wd = Wikidata()

tasks = []


async def addTopic(tid, v, wt, board):
    text = f"== {v.title} == \n\n{v.question}"
    wikitext = await wt.to_wikitext(text)
    new_qid = await wd.add_topic(tid, v.lst_tags, v.formula)
    # new_qid = await wd.add_topic(k, v.lst_tags, v.formula)
    wikitext += '\n\n{{Topic|' + new_qid + '|' + k + '}}'
    # wikitext = await wt.to_wikitext(text)
    id_title = f'Topic {tid}'
    # board.get() #does not work from within async block
    # for top in board.topics():
    #     post: pywikibot.flow.Post = top.root
    #     if id_title == post.get('topic-title-wikitext'):
    #         raise NotImplementedError("PyWikiBot cannot change topics")
    board.new_topic(id_title, wikitext)


board = pywikibot.flow.Board(wd.get_site(), "Formula Topics")
for k, v in formula_reader.map_topics.items():
    wt = Wikitext(wd)
    wt.highlight = [v.formula]
    t = addTopic(k, v, wt, board)
    tasks.append(t)

board = pywikibot.flow.Board(wd.get_site(), "Normal Topics")
for k, v in text_reader.map_topics.items():
    wt = Wikitext(wd)
    wt.highlight = [v.formula]
    t = addTopic(k, v, wt, board)
    tasks.append(t)


async def run():
    await asyncio.gather(*tasks)


asyncio.run(run())
