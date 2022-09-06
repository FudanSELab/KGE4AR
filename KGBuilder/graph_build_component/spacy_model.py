import spacy
from spacy import Language
from graph_build_component.sentenceHandler import SentenceHandler
from graph_build_component.spacy_fixer import SoftwareTextPOSFixer



@Language.factory("fixer_for_pos")
def fixer_for_pos(nlp, name,):
    return SoftwareTextPOSFixer()


@Language.factory("hyphen_handler")
def fixer_for_pos(nlp, name,):
    return SentenceHandler()


def spacy_model():
    nlp = spacy.load('en_core_web_sm', disable=["ner"])
    # special_case = [{ORTH: u"non-null", LEMMA: u"non-null", POS: u"ADJ"}]
    # nlp.tokenizer.add_special_case(u"non null", special_case)
    # special_case = [{ORTH: u"-VERB-", LEMMA: u"-VERB-", POS: u"VERB"}]
    # nlp.tokenizer.add_special_case(u"non null", special_case)

    # from directive.spacy_add_pipe.spacy_fixer import SoftwareTextPOSFixer
    # from directive.spacy_add_pipe.sentenceHandler import SentenceHandler
    nlp.add_pipe("hyphen_handler", before='tagger')
    nlp.add_pipe("fixer_for_pos", after="tagger")
    return nlp
