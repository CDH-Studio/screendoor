from screendoor_app.settings import NLP_MODEL
import re

# fix any false positives of dates being identified as other named entities
def hard_identify_date_ents(doc):
    # for now, only checks the 07/2015-05/2014 regex, but will be expanded
    # as needed
    recovered_dates = re.findall(r"\d*\/\d*-\d*\/\d*", doc.text)

    #creates a list of the dates' start/end positions in the doc
    recovered_dates_locations = []
    for date in recovered_dates:
        start = doc.text.find(date)
        recovered_dates_locations.append((start, start + len(date)))


    new_ents = []

    # Adds the identified dates to the list of new entities
    for date_location in recovered_dates_locations:
        new_ent = doc.char_span(date_location[0], (date_location[1]),
                                label=u'DATEHACK')
        if not (new_ent is None):
            new_ents.append(new_ent)
        else:
            print("ERROR: span not found. help")

    # Loops through the existing entities, leaving them out of the new list
    # if they are contained within the identified date entities
    # thus overriding any faulty NER done on dates
    for ent in doc.ents:
        start = doc.text.find(ent.text)
        end = start + len(ent.text)
        is_distinct = True

        for dates in recovered_dates_locations:
            if start >= dates[0] and end <= dates[1]:
                is_distinct = False
                break
        if is_distinct:
            new_ents.append(ent)

    doc.ents = new_ents
    return doc

# Overrides the date entity recognition, removing false positive dates
# Examples include "over the years", "months", "recently", and other dates
# That we can't extract meaningful information out of
def ensure_valid_date(ents):
    dates = []
    for potential_date in [x for x in ents if 'DATE' in x.label_]:
        if not bool(re.search(r'[0-9]{4}|January|Febuary|March|April|May|June|July|August|September|November|December|last|ago', potential_date.text)):
            continue
        dates.append(potential_date.text)
    return dates

# If there something to pre-append (ie have worked v worked), fix it from
# being passed along as 'worked have', due to the ground-up constructive
# nature of the context generation
def pre_append_to_output(str, preappends):
    if len(str.split()) > 1:
        first, *middle, last = str.split()
        return first + ' ' + ' '.join(middle) + ' ' + ' '.join([x.text for x in preappends]) + ' ' + last
    else:
        return ' '.join([x.text for x in preappends]) + ' ' + str

def navigate_through_tree(root, dates):
    # relations identified as having data we care about, and being paths we
    # want to iterate down, depending on the side that element is on
    accepted_right_relations = ['dobj', 'acomp', 'prep', 'pcomp', 'npadvmod',
                                'appos', 'acl', 'pobj', 'advcl', 'xcomp',
                                'attr', 'nusbj', 'relcl', 'conj', 'ccomp',
                                'advmod', 'agent']
    accepted_left_relations = ['xcomp', 'attr', 'relcl', 'conj']

    # relations identified as containing needed information, that has no
    # relation to the immediate element
    split_branch_relations = ['advcl']

    # relations that contain supplementary information we want, but not as the
    # path we want to create. Mostly for content like "and" and "to".
    look_ahead_relations = ['cc']

    # relations that contain supplementary information we want, but not as the
    # path we want to create. Mostly for content like "and" and "to".
    look_behind_relations = ['aux', 'auxpass', 'nsubj', 'mark', 'advmod', 'amod']

    # Initialize the return object (dates check to remove redundant printing)
    context = ''
    if root.text not in dates:
        context = root.text

    # Note: .children, .lefts, and .rights return generators, not lists
    children = list(root.children)

    additional_iterations = []

    while not (list(children) == []):
        # Initialize list sets of all the identified types, with any needed
        # restrictions to prevent faulty identification (ie, punctuation
        # needing to be directly next to the parent element)
        punctuation = [x for x in root.children if x.dep_ == 'punct' and
                            x.i == root.nbor().i]
        possible_paths = [x for x in root.lefts if
                            x.dep_ in accepted_left_relations] + \
                         [x for x in root.rights if
                            x.dep_ in accepted_right_relations and
                                not x.i > root.i + 5]

        split_branches = [x for x in root.rights if
                            x.dep_ in split_branch_relations and
                                not x.i > root.i + 5]

        append_to_path = [x for x in root.children if
                            x.dep_ in look_ahead_relations and
                                x == root.nbor()]

        deappend_to_path = [x for x in root.lefts if
                            x.dep_ in look_behind_relations and
                                not x.tag_ == 'XX']

        #Construct the context, without iterating down dep_tree
        # print(root)
        # print(punctuation)
        # print(possible_paths)
        # print(split_branches)
        # print(append_to_path)
        # print(deappend_to_path)
        # print('\n\n')
        if deappend_to_path:
            context = pre_append_to_output(context, deappend_to_path)

        if punctuation:
            context += ' ' + ' '.join([x.text for x in punctuation])

        if append_to_path:
            context += ' ' + ' '.join([x.text for x in append_to_path])

        if split_branches:
            additional_iterations = split_branches

        # Iterate through the dep tree, on a first come first serve basis
        # on a left->right basis. Preference hierarchy usually not a concern.
        if possible_paths:

            # Reset the root/children to allow for infinite iteration
            root = possible_paths[0]
            children = list(root.children)

            # Prevents redundant printing
            if root.text not in dates:
                context += ' ' + root.text
        else:
            children = []

        # If we've exhausted our options, we need to check if there's a valid
        # split branch to traverse down
        if children == [] and additional_iterations:
            # Reset the root/children to allow for infinite iteration
            children = additional_iterations
            root = children[0]

            # Hard catch: prevents weird cases
            if root.tag_ == 'VBG':
                break
            if root.text not in dates:
                context += ' ' + root.text

            # Reset the split branch to prevent infinite looping
            additional_iterations = []


    return context


# Remove faulty spacing, hanging punctuation, and other formatting issues
def clean(context):
    if context.endswith(' ,'):
        context = context.replace(' ,', '')
    if context.endswith('('):
        context = context[0:len(context)-1]
    context = context.replace('( ', '(')
    if context.count('(') > context.count(')'):
        context += ')'
    #context = context.replace('as ', '')
    return context

def get_to_tree_root(leaf, dates):
    # note: need a better method to prevent the date
    # from appearing in its own context
    base_leaf = leaf
    stem = leaf.head

    if stem.text in dates:
        return leaf
    while not (leaf.dep_ == 'ROOT'):
        if leaf.head.i > leaf.i + 5 or leaf.head.i < leaf.i - 5:
            return leaf
        # edge case: 'as' identifies somebody introducing their position,
        # which we prefer over their duties, as that will be covered in
        # other nlp functions
        if leaf.text == 'as' or leaf.text == 'As' or  leaf.text == 'at' or leaf.text == 'At':
            return leaf

        # edge case: stem is the highest root element, and only has one child,
        # being the leaf element, and that head contains no usable data.
        # return the leaf
        children = [x for x in list(stem.children) if not x.pos_== 'PUNCT']
        if (len(children) == 1 and
                stem.text == stem.head.text and not (stem.pos_ == 'NOUN' or stem.pos_ == 'PROPN' )):
            if children[0].text == base_leaf.text:
                return leaf

        # edge case: preventative measure of navigating too far up the tree
        # we want to return where we are currently
        if stem.dep_ == 'nsubj' or stem.dep_ == 'conj' or stem.dep_ == 'npadvmod':
            return stem

        # edge case: navigating too far up the tree
        if leaf.dep_ == 'ccomp':
            return leaf

        # edge case: prevents retread of already supplied data
        if stem.text in dates:
            return leaf

        # If all is good, move 'up' one level and continue going
        leaf = stem
        stem = stem.head
    return stem


def iterate_through_dep_tree(dep_tree):
    # create a list of all the date entities tagged by the ner process
    dates = ensure_valid_date(dep_tree.ents)

    contexts = []

    for leaf in dep_tree:

        # If we're currently looking at a date's context
        if leaf.text in dates:
            # Get to the head of the dep_tree
            root = get_to_tree_root(leaf, dates)
            # now that we have the head of the date entity,
            # navigate through it for the context of the current date
            contexts.append(clean(leaf.text + ": " + navigate_through_tree(root, dates)))
    return contexts


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
# (eg 'Statistics Canada', rather than 'Statistics' 'Canada' (as can happen))
def squash_named_entities(doc):
    spans = list(doc.noun_chunks) + list(doc.ents)
    spans = filter_spans(spans)
    filtered_dates = [x for x in doc.noun_chunks for y in doc.ents if
            y.text in x.text and 'DATE' in y.label_]
    spans = [x for x in spans if x not in filtered_dates]
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)


def determine_named_entities(text):
    doc = NLP_MODEL(text)
    squash_named_entities(doc)
    hard_identify_date_ents(doc)
    return doc


def extract_dates(text):
    doc = determine_named_entities(text)
    return iterate_through_dep_tree(doc)


def get_identified_dates(doc):
    squash_named_entities(doc)
    hard_identify_date_ents(doc)
    return (x for x in doc.ents if 'DATE' in x.label_)