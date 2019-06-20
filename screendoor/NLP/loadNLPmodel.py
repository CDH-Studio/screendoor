import spacy
from spacy.pipeline import EntityRuler

def init_spacy_module():
    nlp = spacy.load('en_core_web_sm')
    ruler = EntityRuler(nlp, overwrite_ents=True)
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer, first=True)

    # custom date entity patterns
    # to be iterated on
    patterns = [
        # Example catches:
        #   between June 2015 until the day I quit in May 2018
        #   from 2014, lasting 5 years
        #   since April 2011
        {'label': 'DATE1', 'pattern': [
            {'LOWER': {'REGEX': 'from|between|starting|since'}, 'OP': '?'},
            {'ENT_TYPE': 'DATE'},
            {'LOWER': {'REGEX': '[^a.);:\n]'}, 'OP': '*'},
            {'ENT_TYPE': 'DATE'},
            {'LOWER': {'REGEX': 'until|to'}, 'OP': '?'},
            {'LOWER': {'REGEX': 'the'}, 'OP': '?'},
            {'LOWER': {'REGEX': 'present|current|today|now'}, 'OP': '?'}
        ]},

        # Example catches:
        #   starting December 31st until the present
        #   from July 2011 to now
        {'label': 'DATE2', 'pattern': [
            {'LOWER': {'REGEX': 'from|between|starting'}, 'OP': '?'},
            {'ENT_TYPE': 'DATE', 'OP': '+'},
            {'LOWER': {'REGEX': 'until|to'}},
            {'LOWER': {'REGEX': 'present|current|today|now'}}]},

        # Example catches:
        #   2015 - present
        #   2016 - current
        #   from 2015 - today
        #
        {'label': 'DATE4', 'pattern': [
            {'LOWER': {'REGEX': 'from'}, 'OP': '?'},
            {'POS': 'NUM', 'SHAPE': 'dddd'},
            {'LOWER': '-'},
            {'LOWER': {'REGEX': 'present|current|today|now'}}]},

        # Example catches:
        #   since April 31st 2018
        #   since June 2015
        {'label': 'DATE3', 'pattern': [
            {'LOWER': 'since'},
            {'ENT_TYPE': 'DATE'}]},

        # Example catches:
        #   2011-2015
        {'label': 'DATE5', 'pattern': [
            {'OP': '?'},
            {'POS': 'NUM', 'SHAPE': 'dddd'},
            {'LOWER': '-'},
            {'OP': '?'},
            {'POS': 'NUM', 'SHAPE': 'dddd'}]},

        # Example catches:
        #   3-year
        {'label': 'DATE6', 'pattern': [
            {'LOWER': {'REGEX': '\d*-year'}}]},

        # Example catches:
        #   07/2015 - 09/2016
        {'label': 'DATE7', 'pattern': [
            {'LOWER': {'REGEX': '\d*\/\d*'}},
            {'LOWER': '-'},
            {'LOWER': {'REGEX': '\d*\/\d*'}}]},

        # Example catches:
        #   07/2015 - 09/2016
        {'label': 'DATE7', 'pattern': [
            {'LOWER': 'as'},
            {'LOWER': 'of'},
            {'ENT_TYPE': 'DATE'}]},

    ]

    # want it last, as overwrite ents are on (otherwise the standard NER
    # overrides the custom patterns
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler, last=True)

    # merges all entities into single entities. Want it after the NER process
    merge_ents = nlp.create_pipe('merge_entities')
    nlp.add_pipe(merge_ents, last=True)
    return nlp