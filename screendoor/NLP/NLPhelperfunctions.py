import spacy
from spacy.pipeline import EntityRuler
import re


def init_spacy_module():
    nlp = spacy.load('en_core_web_sm')
    months_regex = '\bJanuary\b|\bFebruary\b|\bMarch\b|\bApril\b|' \
                   '\bMay\b|\bJune\b|\bJuly\b|\bAugust\b|\bSeptember\b|' \
                   '\bNovember\b|\bDecember\b|\bJan\b|\bFeb\b|\bMar\b|' \
                   '\bApr\b|\bJun\b|\bJul\b|\bAug\b|\bSept\b|\bNov\b|\bDec\b|'
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
            {'LOWER': {'REGEX': 'from|starting|since'}, 'OP': '?'},
            {'ENT_TYPE': 'DATE', 'OP': '+'},
            {'LOWER': {"NOT_IN": [',', '.', '(', ')', ';', ':', '\n', 'and']}, 'OP': '*'},
            {'ENT_TYPE': 'DATE', 'OP': '+'},
            {'LOWER': {'REGEX': 'until|to'}, 'OP': '?'},
            {'LOWER': {'REGEX': 'the'}, 'OP': '?'},
            {'LOWER': {'REGEX': 'present|current|today|now'}, 'OP': '?'}
        ]},

        {'label': 'DATE1A', 'pattern': [
            {'LOWER': {'REGEX': 'between'}, 'OP': '?'},
            {'ENT_TYPE': 'DATE', 'OP': '+'},
            {'LOWER': 'and'},
            {'ENT_TYPE': 'DATE', 'OP': '+'}
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
        #   from 2011-2015
        #   between March 2011 - April 2015
        {'label': 'DATE5', 'pattern': [
            {'LOWER': {'REGEX': 'from|between|starting'}, 'OP': '?'},
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
        {'label': 'DATE8', 'pattern': [
            {'LOWER': {'REGEX': months_regex}},
            {'POS': 'NUM', 'SHAPE': 'dd'},
            {'LOWER': '-'},
            {'LOWER': {'REGEX': months_regex}},
            {'POS': 'NUM', 'SHAPE': 'dd'}]},

    ]

    # want it last, as overwrite ents are on (otherwise the standard NER
    # overrides the custom patterns
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler, last=True)

    # merges all entities into single entities. Want it after the NER process
    merge_ents = nlp.create_pipe('merge_entities')
    nlp.add_pipe(merge_ents, last=True)
    return nlp


# Remove faulty spacing, hanging punctuation, and other formatting issues
# so the return value displays all nice
def clean_output(context):
    if context is None:
        return None
    if context.endswith(' ,'):
        context = context.replace(' ,', '')
    if context.endswith('('):
        context = context[0:len(context)-1]
    if context.endswith(' :'):
        context = context[0:len(context)-2]
    if context.startswith(' '):
         context = context[1:len(context)]
    context = context.replace('( ', '(')
    context = context.replace(' )', ')')
    context = context.replace(" '", "'")
    context = context.replace(" , ", ", ")
    context = context.replace(" - ", "-")
    context = context.replace(" .", ".")
    context = context.replace("..", ".")
    if context.count('(') > context.count(')'):
        context += ')'
    return context

# Attempts to filter out any bad subjects (note: absence of a subject assumes
# the applicant is referring to themselves
def remove_bad_subjects(sent):
    test2 = [x.text for x in sent if x.dep_ == 'ROOT'
             and x.pos_ in ['NOUN', 'DET']]
    if test2:
        return False

    test = [x.text for x in sent if x.dep_ == 'nsubj'
            or x.dep_ == 'nsubjpass']
    if test == []:
        return True
    else:
        pronoun_check = [item for sublist in
                         [re.findall(r'\bI\b|\bwe\b|\bWe\b', x) for x in test]
                         for item in sublist]
        possessive_check = [item for sublist in
                         [re.findall(r'\b[a|A|m|M][y|s]\b', x) for x in test]
                         for item in sublist]
        if not (pronoun_check + possessive_check == []):
            return True
    return False

def format_text(text):
    return re.sub(r"\n(?=[A-Z])", ". ", text).replace(". ", ".")\
        .replace(".", ". ").replace("\n\n", ". ").replace(' - ', '-')\
        .replace('-', ' - ').replace("..", ".")