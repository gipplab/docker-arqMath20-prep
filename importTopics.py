
from Topics.TopicReader import TopicReader
from pyWikiBot import to_wikitext

formula_reader = TopicReader('/data/Topics_V1.1.xml')
text_reader = TopicReader('/data/Topics_V2.0.xml')

for k, v in formula_reader.map_topics.items():
    print(k, to_wikitext(v.title) )
