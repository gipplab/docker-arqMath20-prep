import asyncio

from Topics.TopicReader import TopicReader
from Wikitext.Wikitext import Wikitext

formula_reader = TopicReader('/data/Topics_V1.1.xml')
text_reader = TopicReader('/data/Topics_V2.0.xml')

texts = []
for k, v in formula_reader.map_topics.items():
    wt = Wikitext()
    wt.highlight = [v.formula]
    text = texts.append(wt.to_wikitext(v.title + v.question))


async def run():
    results = await asyncio.gather(*texts)
    for res in results:
        if 0 > res.find('highlight'):
            print(res)


asyncio.run(run())
