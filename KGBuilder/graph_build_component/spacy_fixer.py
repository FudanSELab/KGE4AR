from nltk import WordNetLemmatizer
from spacy.tokens.doc import Doc

from script.word_util import WordUtil

"""
spacy相关的工具类
"""


class SoftwareTextPOSFixer:
    lemmatizer = WordNetLemmatizer()
    verb_set = {'appends', 'reads'}
    token2pos_map = {
        'null': "NOUN"
    }

    def __init__(self, ):
        pass

    def __call__(self, doc: Doc):
        if doc is None or len(doc) == 0:
            return doc
        first_token = doc[0]

        attrs = None
        if first_token.text.lower() == "return":
            attrs = {"LEMMA": "return", "TAG": "VB", "POS": "VERB"}
        if first_token.text.lower() == "returns":
            attrs = {"LEMMA": "return", "TAG": "VBZ", "POS": "VERB"}
        # if first_token.text.lower() == "appends":
        #     attrs = {"LEMMA": "append", "TAG": "VBZ", "POS": "VERB"}

        if attrs is not None:
            with doc.retokenize() as retokenizer:
                retokenizer.merge(doc[0:1], attrs=attrs)
            return doc

        # todo: 考虑动词被动？
        if WordUtil.couldBeVerb(doc[0].text) and doc[0].pos_ == "ADV":
            lemma = SoftwareTextPOSFixer.lemmatizer.lemmatize(first_token.text, "v")
            if lemma == first_token.text.lower():
                tag = "VB"
            else:
                tag = "VBZ"

            attrs = {"LEMMA": lemma, "POS": "VERB",
                     "TAG": tag}
            with doc.retokenize() as retokenizer:
                retokenizer.merge(doc[0:1], attrs=attrs)
            return doc

        # 被动形式
        # if WordUtil.couldBeVerb(doc[0].text) and doc[0].tag_ == "VBD":
        #     lemma = SoftwareTextPOSFixer.lemmatizer.lemmatize(first_token.text, "v")
        #     if lemma == first_token.text.lower():
        #         tag = "VB"
        #     else:
        #         tag = "VBZ"
        #
        #     attrs = {"LEMMA": lemma, "POS": "VERB",
        #              "TAG": tag}
        #     with doc.retokenize() as retokenizer:
        #         retokenizer.merge(doc[0:1], attrs=attrs)
        #     return doc

        return doc
