class Topic:
    """
    This class shows a topic for task 1. Each topic has an topic_id which is str, a title and question which
    is the question body and a list of tags.
    """

    def __init__(self, topic_id, title, question, tags, formula=None):
        self.topic_id = topic_id
        self.title = title
        self.question = question
        self.lst_tags = tags
        self.formula = formula


