
from Topics.TopicReader import TopicReader

formula_reader = TopicReader('/data/Topics_V1.1.xml')
for k, v in formula_reader.map_topics.items():
    print(k, v.formula)
