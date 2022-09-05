from nltk.corpus import wordnet as wn


class WordUtil:
    @staticmethod
    def couldBeVerb(word):
        """
        check if a word could be a verb
        :param word:
        :return:
        """
        pairs = [tuple(synset.name().split(".")[:2]) for synset in wn.synsets(word)]
        tag_count = {}
        for name, tag in pairs:
            tag_count[tag] = tag_count.get(tag, 0) + 1
        if len(tag_count) == 0:
            return False
        if "v" in tag_count:
            return True
        return False

    @staticmethod
    def couldBeNoun(word):
        """
        check if a verb could be noun
        :param word:
        :return:
        """
        pairs = [tuple(synset.name().split(".")[:2]) for synset in wn.synsets(word)]
        tag_count = {}
        for name, tag in pairs:
            tag_count[tag] = tag_count.get(tag, 0) + 1
        if len(tag_count) == 0:
            return False
        if "n" in tag_count:
            return True
        return False

    @staticmethod
    def couldBeADJ(word):
        """
        check if a word could be adj
        :param word:
        :return:
        """
        pairs = [tuple(synset.name().split(".")[:2]) for synset in wn.synsets(word)]
        tag_count = {}
        for name, tag in pairs:
            tag_count[tag] = tag_count.get(tag, 0) + 1
        if len(tag_count) == 0:
            return False
        if "a" in tag_count or "s" in tag_count:
            return True
        return False
