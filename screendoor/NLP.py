import spacy
from spacy.lang.en import English
from spacy.pipeline import EntityRuler
from spacy import displacy
from spacy.symbols import *


def init_spacy_module():
    nlp = spacy.load('en_core_web_sm')
    ruler = EntityRuler(nlp, overwrite_ents=True)

    # custom date entity patterns
    # to be iterated on
    patterns = [
        {'label': 'DATE1', 'pattern': [
            {'LOWER': {'REGEX': 'from|between|starting|since'}, 'OP': '?'},
            {'ENT_TYPE': 'DATE'},
            {'LOWER': {'REGEX': '[^.);:\n]'}, 'OP': '*'},
            {'ENT_TYPE': 'DATE'},
            {'LOWER': {'REGEX': 'until|to'}, 'OP': '?'},
            {'LOWER': {'REGEX': 'the'}, 'OP': '?'},
            {'LOWER': {'REGEX': 'present|current|today|now'}, 'OP': '?'}
        ]},

        {'label': 'DATE2', 'pattern': [
            {'LOWER': {'REGEX': 'from|between|starting'}, 'OP': '?'},
            {'ENT_TYPE': 'DATE', 'OP': '+'},
            {'LOWER': {'REGEX': 'until|to'}},
            {'LOWER': {'REGEX': 'present|current|today|now'}}]},

        {'label': 'DATE4', 'pattern': [
            {'POS': 'NUM'},
            {'LOWER': '-'},
            {'LOWER': {'REGEX': 'present|current|today|now'}}]},

        {'label': 'DATE4', 'pattern': [
            {'LOWER': {'REGEX': 'from'}, 'OP': '?'},
            {'POS': 'NUM', 'SHAPE': 'dddd'},
            {'LOWER': '-'},
            {'LOWER': {'REGEX': 'present|current|today|now'}}]},

        {'label': 'DATE3', 'pattern': [
            {'LOWER': 'since'},
            {'ENT_TYPE': 'DATE'}]},

        {'label': 'DATE5', 'pattern': [
            {'POS': 'NUM', 'SHAPE': 'dddd'},
            {'LOWER': '-'},
            {'POS': 'NUM', 'SHAPE': 'dddd'}]},
    ]

    # want it last, as overwrite ents are on (otherwise the standard ner
    # overrides the custom patterns
    ruler.add_patterns(patterns)
    ruler.to_disk('./patterns.jsonl')
    nlp.add_pipe(ruler, last=True)

    merge_ents = nlp.create_pipe('merge_entities')
    nlp.add_pipe(merge_ents)
    return nlp


# accepted dependencies we want to iterate down
# NOTE: iteration is done on a first come first serve basis
# due to the method of 'recursively' looping
# logic needs to be redone to (hopefully) include a preference hierarchy
# and allow for multiple children to be checked at once
def navigate_through_tree(root, context):
    accepted_relations = ['dobj', 'acomp', 'pcomp', 'npadvmod', 'appos',
                          'pobj', 'prep', 'conj', 'advcl', 'nsubj']

    # note: rights returns the children to the right of the element
    # may be removed if a way to identify the best path to take is found
    children = list(root.rights)
    while not (children == []):
        for p in children:
            # aside from the valid relations:
            #   - accept closing brackets (as punctuation is not allowed)
            #   - disallow spaces (caused by bad data)
            if ((p.dep_ in accepted_relations or p.text is ')') and not (
                    p.pos_ == 'SPACE')):
                context += p.text + ' '
                # resetting children and breaking allows the list to continue
                # for as long as there are valid elements to iterate over
                children = list(p.rights)
                break
            children = []
    return context


def get_to_tree_root(leaf):
    # note: need a better method to prevent the date
    # from appearing in its own context
    base_leaf = leaf
    stem = leaf.head
    # running .head on the head of the tree returns the element again
    # rather than an empty element, like you might expect
    while not (stem.text == leaf.text):
        # edge case: stem is the highest root element, and only has one child,
        # being the leaf element. we want the leaf to be our top level element
        children = list(stem.children)
        if (len(children) == 1 and
                not stem.head.text == stem.head.head.text):
            if children[0].text == base_leaf.text:
                return leaf

        # edge case: navigating too far up the tree
        # we want to return where we are currently
        if stem.dep_ == 'nsubj':
            return stem
        leaf = stem
        stem = stem.head
    return stem


def iterate_through_dep_tree(dep_tree):
    # create a list of all the date entities tagged by the ner process
    dates = []
    for ent in dep_tree.ents:
        if 'DATE' in ent.label_:
            dates.append(ent.text)

    # return object
    context_list = []

    for leaf in dep_tree:
        # If we're currently looking at a date's context
        if leaf.text in dates:
            # Get to the head of the dep_tree
            root = get_to_tree_root(leaf)

            # make sure the display looks correct
            if not root == leaf:
                context = (leaf.text + ': ' + root.text + ' ')
            else:
                context = (leaf.text + ': ')

            # now that we have the head of the tree,
            # navigate through it for the context of the current date
            context_list.append(navigate_through_tree(root, context))

    return context_list


# Prevents crash: retokenizer only works on disjoint sets
def filter_spans(spans):
    # Filters a sequence of spans so they don't contain overlaps
    get_sort_key = lambda span: (span.end - span.start, span.start)
    sorted_spans = sorted(spans, key=get_sort_key, reverse=True)
    result = []
    seen_tokens = set()
    for span in sorted_spans:
        if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
            result.append(span)
            seen_tokens.update(range(span.start, span.end))
    return result


# combine named entities into single tokens
# (ie 'April 2015 to present', rather than 'April' '2015' 'to' 'present')
def squash_named_entities(doc):
    spans = list(doc.ents) + list(doc.noun_chunks)
    spans = filter_spans(spans)
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)


# base function to call
# name temporary
def test_spacy_functionality(text):
    nlp = init_spacy_module()
    doc = nlp(text)
    squash_named_entities(doc)

    for ent in doc.ents:
        print([(ent.text, ent.label_)])

    print('\n\n')

    print(iterate_through_dep_tree(doc))
    print('\n\n')
