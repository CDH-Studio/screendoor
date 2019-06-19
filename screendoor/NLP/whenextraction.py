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

        new_ent = doc.char_span(date_location[0], date_location[1],
                                label=u'DATEHACK')
        if not (new_ent is None):
            new_ents.append(new_ent)

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

# NOTE: each relation has been identified has having 2 or more instances where
# the case doesnt return bad data. Cases where it does not return what is
# expected need to be looked at further as either refinements or edge cases.
# test suite to come
def navigate_through_tree(root, dates):
    context = ''
    if not (root.text in dates):
        context = root.text + ' '
    # relations identified as having data we care about, and being paths we
    # want to iterate down
    accepted_relations = ['dobj', 'acomp', 'prep', 'pcomp', 'npadvmod', 'appos',
                          'pobj', 'conj', 'advcl', 'nsubj', 'xcomp', 'attr',
                          'relcl']

    # relations that contain supplemntary information we want, but not as the
    # path we want to create. Mostly for content like "and" and "to".
    look_ahead_relations = ['cc', 'conj', 'punct']

    # relations that return bad data if they are found to the left of the root
    # mainly prevents badly formatted data
    prohibited_left_relations = ['prep', 'advcl']

    # tags that under no circumstance should be allowed to be treated as valid
    # paths.
    prohibited_pos_tags = ['SPACE', 'PRON', 'X']
    subject = None

    children = list(root.children)

    # checks for a split branch
    prep_list = [x for x in children if x.dep_ == 'prep' and len(children) > 1]
    additional_branch = None
    # If one is found, grab it (will always be first+only element), and disallow
    # if from being iterated through
    if not prep_list == []:
        additional_branch = prep_list[0]
        children.remove(additional_branch)

    while not (children == []):
        for p in children:
            if ((p.dep_ in prohibited_left_relations) and p in root.lefts) and not list(p.children) == []:
                continue

            if (p.dep_ in look_ahead_relations) and not list(p.children) == []:
                context += p.text + ' '
                continue

            if (p.dep_ in accepted_relations and
                    not (p.pos_ in prohibited_pos_tags) and
                    (not (p.text in dates) or p.dep_ == 'dobj')):
                context += p.text + ' '
                # resetting children and breaking allows the list to continue
                # for as long as there are valid elements to iterate over
                children = list(p.children)
                break
            children = []

    # Deals with split branch logic: if the sentence contains information in two
    # trees, return both trees appended together left to right
    if not (additional_branch == None):
        context += navigate_through_tree(additional_branch, dates)
    return context


def get_to_tree_root(leaf, dates):
    # note: need a better method to prevent the date
    # from appearing in its own context
    base_leaf = leaf
    stem = leaf.head
    while not (stem.dep_ == 'ROOT'):
        # edge case: 'as' identifies somebody introducing their position,
        # which we prefer over their duties, as that will be covered in
        # other nlp functions
        if leaf.text == 'as' or leaf.text == 'As':
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
    dates = []
    for ent in dep_tree.ents:
        if 'DATE' in ent.label_:
            dates.append(ent.text)

    contexts = {}


    for leaf in dep_tree:

        # If we're currently looking at a date's context
        if leaf.text in dates:
            # Get to the head of the dep_tree
            root = get_to_tree_root(leaf, dates)
            # now that we have the head of the date entity,
            # navigate through it for the context of the current date
            contexts[leaf.text] = navigate_through_tree(root, dates)
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
# (ie 'April 2015 to present', rather than 'April' '2015' 'to' 'present')
def squash_named_entities(doc):
    spans = list(doc.noun_chunks) + list(doc.ents)
    spans = filter_spans(spans)
    with doc.retokenize() as retokenizer:
        for span in spans:
            #if not (span.text in x.text for x in list(doc.ents)):
                retokenizer.merge(span)



def extract_dates(text):
    doc = NLP_MODEL(text)
    squash_named_entities(doc)
    hard_identify_date_ents(doc)
    return iterate_through_dep_tree(doc)