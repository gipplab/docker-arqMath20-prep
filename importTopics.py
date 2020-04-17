from Topics.TopicReader import TopicReader
from Wikitext.Wikitext import Wikitext

formula_reader = TopicReader('/data/Topics_V1.1.xml')
text_reader = TopicReader('/data/Topics_V2.0.xml')
wt = Wikitext()

for k, v in formula_reader.map_topics.items():
    wt.highlight = [v.formula]
    text = wt.to_wikitext(v.title + v.question)
    if 0 > text.find('highlight'):
        print(k, wt.to_wikitext(v.title + v.question))
