import xml.etree.ElementTree as ET
from typing import Optional

from Topic import Topic


class TopicReader:
    """
    This class takes in the topic file path and read all the topics into a map. The key in this map is the topic id
    and the values are Topic which has 4 attributes: id, title, question and list of tags for each topic.

    To see each topic, use the get_topic method, which takes the topic id and return the topic in Topic object and
    you have access to the 4 attributes mentioned above.
    """

    def __init__(self, topic_file_path):
        self.map_topics = self.__read_topics(topic_file_path)

    def __read_topics(self, topic_file_path):
        map_topics = {}
        tree = ET.parse(topic_file_path)
        root = tree.getroot()
        for child in root:
            topic_id = child.attrib['number']
            title = child.find('Title').text
            question = child.find('Question').text
            lst_tag = child.find('Tags').text.split(",")
            formula = child.find('Formula_Id')
            formula_tag = None
            if formula is not None:
                formula_tag = formula.text
            map_topics[topic_id] = Topic(topic_id, title, question, lst_tag, formula_tag)
        return map_topics

    def get_topic(self, topic_id) -> Optional[Topic]:
        if topic_id in self.map_topics:
            return self.map_topics[topic_id]
        return None
