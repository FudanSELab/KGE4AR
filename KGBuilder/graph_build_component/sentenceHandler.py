from nltk import WordNetLemmatizer
from spacy.tokens.doc import Doc

"""
spacy相关的工具类
"""


class SentenceHandler:
    __HyphenHandler = 'hyphen_handler'
    lemmatizer = WordNetLemmatizer()

    def __init__(self, ):
        pass

    @staticmethod
    def kuohao_fenci(doc: Doc):
        """
        这个方法用于处理分词的结果
        :param doc:
        :return:
        """

    @staticmethod
    def continuous_symbol_processing(doc: Doc, op):
        hyphen_index = []
        hyphen_index_start = -1
        length = len(doc)
        for i, token in enumerate(doc):
            if op == token.text:
                if hyphen_index_start == -1:
                    hyphen_index_start = i
            else:
                if hyphen_index_start != -1:
                    if i != length - 1:
                        if doc[i + 1].text != op:
                            hyphen_index.append((hyphen_index_start, i))
                            hyphen_index_start = -1
                        else:
                            # 将连续的op合并
                            continue
                    else:
                        hyphen_index.append((hyphen_index_start, i))
                        hyphen_index_start = -1

        with doc.retokenize() as retokenizer:
            for start, end in hyphen_index:
                # 如果是紧邻的连字符则认为是同一个词汇，否则将其拆分
                attrs = {"LEMMA": doc[start: end].lemma_}
                retokenizer.merge(doc[start: end], attrs=attrs)
        return doc

    @staticmethod
    def hyphen_processing(doc: Doc, op):
        """
        连字符的处理
        """
        hyphen_index = []
        hyphen_index_start = -1
        length = len(doc)
        for i, token in enumerate(doc):
            if op == token.text:
                if hyphen_index_start == -1:
                    hyphen_index_start = i - 1
            else:
                if hyphen_index_start != -1:
                    if i != length - 1:
                        if doc[i + 1].text != op:
                            hyphen_index.append((hyphen_index_start, i))
                            hyphen_index_start = -1
                        else:
                            # 将连续的op合并
                            continue
                    else:
                        hyphen_index.append((hyphen_index_start, i))
                        hyphen_index_start = -1

        with doc.retokenize() as retokenizer:
            for start, end in hyphen_index:
                if doc[start + 1].idx - doc[start].idx == 1 and doc[end].idx - doc[end - 1].idx == 1:
                    # 如果是紧邻的连字符则认为是同一个词汇，否则将其拆分
                    attrs = {"LEMMA": doc[start:(end + 1)].lemma_}
                    retokenizer.merge(doc[start:end + 1], attrs=attrs)
        return doc

    def __call__(self, doc: Doc):
        """
        合并连字符，如fail-fast在tokenize之后会分成fail - fast三个，合并之后变为fail-fast
        :param doc:
        :return:
        """

        # 处理相同的连续字符: -, = ,+
        doc = SentenceHandler.hyphen_processing(doc, '-')
        doc = SentenceHandler.continuous_symbol_processing(doc, '=')
        doc = SentenceHandler.continuous_symbol_processing(doc, '+')
        doc = SentenceHandler.continuous_symbol_processing(doc, ':')
        #
        # # 处理不同的连续操作符: >=, <=, !=
        # doc = SentenceHandler.

        # todo： 对于引号内的文本，将其作为一个整体， 词性标注为“引用”。

        # 添加对于null的处理
        for i, token in enumerate(doc):
            if SentenceHandler.lemmatizer.lemmatize(token.text, "v") == "null":
                with doc.retokenize() as retokenizer:
                    attrs = {
                        "LEMMA": "null",
                        "POS": "NOUN",
                        "TAG": "NN",
                    }
                    retokenizer.merge(doc[i:i + 1], attrs=attrs)

        method_left_brace_cache_index = -1
        left_angle_bracket = -1
        angle_brackets_list = []
        method_brace_pair_list = []
        for i, token in enumerate(doc):
            # 添加了对method name的处理
            if "<" == token.text:
                if i > 0 and doc[i - 1].text != ">":
                    left_angle_bracket = i - 1
                else:
                    left_angle_bracket = i
            elif "<" in token.text:
                left_angle_bracket = i

            if ">" == token.text and left_angle_bracket != -1:
                angle_brackets_list.append((left_angle_bracket, i))
                left_angle_bracket = -1
        # print(method_brace_pair_list)
        with doc.retokenize() as retokenizer:
            for star_index, end_index in angle_brackets_list:
                attrs = {"LEMMA": " ".join([token.text for token in doc[(star_index):(end_index + 1)]]),
                         "POS": "NOUN",
                         "TAG": "NN",
                         }
                retokenizer.merge(doc[star_index:end_index + 1], attrs=attrs)

        for i, token in enumerate(doc):
            # 添加了对method name的处理
            if "(" == token.text:
                if i > 0 and doc[i - 1].text != ")" and doc[i - 1].text != ".":
                    method_left_brace_cache_index = i - 1
                else:
                    method_left_brace_cache_index = i
            elif "(" in token.text:
                method_left_brace_cache_index = i

            if ")" == token.text and method_left_brace_cache_index != -1:
                method_brace_pair_list.append((method_left_brace_cache_index, i))
                method_left_brace_cache_index = -1
        # print(method_brace_pair_list)
        with doc.retokenize() as retokenizer:
            for star_index, end_index in method_brace_pair_list:
                span = doc[star_index:(end_index + 1)]
                if not SentenceHandler.is_complete_sentence(span):
                    attrs = {"LEMMA": " ".join([token.text for token in doc[(star_index):(end_index + 1)]]),
                             "POS": "NOUN",
                             "TAG": "NN",
                             }
                    retokenizer.merge(doc[star_index:end_index + 1], attrs=attrs)

        return doc

    @staticmethod
    def is_complete_sentence(doc):
        root_flag = False
        nusj_flag = False
        for token in doc:
            if token.tag_.startswith('NN'):
                nusj_flag = True
            if token.tag_.startswith('VB'):
                root_flag = True
        if root_flag and nusj_flag:
            return True
        return False

    @staticmethod
    def merge_verb_prep(doc: Doc):
        for token in doc:
            # print(token.text)
            if token.dep_ == 'ROOT' and token.pos_ == 'VERB' and token.tag_ != 'VBN':
                # print(token.text)
                if token.i < len(doc) - 1:
                    if doc[token.i + 1].dep_ == 'prep' and doc[token.i + 1].head == token:
                        with doc.retokenize() as retokenizer:
                            attrs = {"LEMMA": " ".join([token.lemma_, doc[token.i + 1].lemma_]),
                                     "POS": "VERB",
                                     "TAG": token.tag_
                                     }
                            retokenizer.merge(doc[token.i:token.i + 2], attrs=attrs)
                        if token.i < len(doc) - 1:
                            # print(doc[token.i+1])
                            if doc[token.i + 1].dep_ == 'pobj' and doc[token.i + 1].pos_ == 'NOUN':
                                with doc.retokenize() as retokenizer:
                                    attrs = {"DEP": "dobj"
                                             }
                                    retokenizer.merge(doc[token.i + 1:token.i + 2], attrs=attrs)
                    break
        return doc


    @staticmethod
    def class_name_tag(doc: Doc):
        """
        为class_name自定义词性标注
        :param doc:
        :return:
        """
        for i in range(0, len(doc)):
            # 因为class_name可能出现RC2StringBuilder这种类型，2,4不一定就是表示to和for
            # if spacy_doc[i].text == "2" and i != 0 and len(spacy_doc) - 1:
            #     spacy_doc[i].lemma_ = "to"
            #     spacy_doc[i].pos_ = "ADP"
            #     spacy_doc[i].tag_ = "IN"
            #
            # if spacy_doc[i].text == "4" and i != 0 and len(spacy_doc) - 1:
            #     spacy_doc[i].lemma_ = "for"
            #     spacy_doc[i].pos_ = "ADP"
            #     spacy_doc[i].tag_ = "IN"

            if doc[i].text.lower() == "to":
                doc[i].lemma_ = "to"
                doc[i].pos_ = "ADP"
                doc[i].tag_ = "IN"

            if doc[i].text.lower() in ["id", "ID", "Id"]:
                doc[i].lemma_ = "id"
                doc[i].pos_ = "NOUN"
                doc[i].tag_ = "NN"

        if doc[-1].pos_ == 'VERB':
            doc[-1].pos_ = 'NOUN'
            doc[-1].tag_ = 'NN'

        return doc
