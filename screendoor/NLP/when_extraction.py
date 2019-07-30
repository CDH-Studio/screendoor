from screendoor_app.settings import NLP_MODEL
from .helpers.general_helpers import remove_bad_subjects, get_first_elem_or_none, print_if_debug, fuzzy_search_extract_in_orig_doc
from .helpers.format_text import post_nlp_format_input, strip_faulty_formatting
from .helpers.when_extraction_helpers import squash_named_entities, get_valid_dates, hard_identify_date_ents
import re

# relations that contain supplementary information we want, but not as the
# path we want to create. Mostly for content like "and" and "to".
prepend_relations = ['aux', 'auxpass', 'nsubj', 'nsubjpass', 'mark',
                             'advmod', 'amod', 'compound', 'poss', 'nmod',
                             'compound', 'neg']

append_relations = ['cc', 'prt', 'case', 'nummod']

# relations identified as containing needed information, that has no
# relation to the immediate element
additional_iteration_relations = ['advcl']

# relations identified as having data we care about, and being paths we
# want to iterate down, depending on the side that element is on
accepted_right_relations = ['dobj', 'acomp', 'prep', 'pcomp', 'npadvmod',
                            'appos', 'acl', 'pobj', 'advcl', 'xcomp',
                            'attr', 'nusbj', 'conj', 'ccomp',
                            'advmod', 'agent']
accepted_left_relations = ['xcomp', 'attr', 'relcl', 'conj', 'advcl', 'meta']


# Makes sure any punctuation is not lost in the dep_tree navigation (as punctuation are tokens just as
# any other word).
def add_punctuation_to_extract(token, extract, dates):
    punctuation_to_add_to_extract = [x for x in token.children if x.dep_ == 'punct' and
                                     x.i == token.nbor().i and x.text not in dates
                                     and x.text not in ['(']]

    if punctuation_to_add_to_extract:
        extract += ' ' + ' '.join([x.text for x in punctuation_to_add_to_extract])
    return extract


# Adds any text located before the current word, which while not being valid dep_tree navigation
# paths, are still needed to ensure the output matches the original answer.
def prepend_text_to_extract(token, extract, dates):
    words_to_prepend_to_extract = [x for x in token.lefts if
                                   x.dep_ in prepend_relations and
                                   not x.tag_ == 'XX' and x.text not in dates]

    # Makes sure that the prepend words get added before the last word, rather
    # than naively just adding to the start of the entire constructed extract.
    if len(extract.split()) > 1:
        first, *middle, last = extract.split()
        return first + ' ' + \
               ' '.join(middle) + ' ' + \
               ' '.join([x.text for x in words_to_prepend_to_extract]) + \
               ' ' + last
    else:
        return ' '.join([x.text for x in words_to_prepend_to_extract]) + \
               ' ' + extract


# Adds any text located after the current word, which while not being valid dep_tree navigation
# paths, are still needed to ensure the output matches the original answer.
def append_text_to_extract(token, extract, dates):
    words_to_append_to_extract = [x for x in token.children if
                                  x.dep_ in append_relations and
                                  x == token.nbor() and x.text not in dates]

    return extract + ' ' + ' '.join([x.text for x in words_to_append_to_extract])


# Searches for any 'split branches', to avoid dead-ending dep_tree navigation when
# valuable information remains to be processed.
def check_for_additional_iterations(token, dates):
    words_for_additional_iteration = [x for x in token.rights if
                                      x.dep_ in additional_iteration_relations and
                                      not x.i > token.i + 7 and x.text not in dates]

    return get_first_elem_or_none(words_for_additional_iteration)


# Searches for tokens that are determined to be valid iteration paths for
# dep_tree navigation.
def determine_next_word_to_navigate_to(token, dates):
    possible_paths = [x for x in token.lefts if
                      x.dep_ in accepted_left_relations and x.text not in dates] + \
                     [x for x in token.rights if
                      x.dep_ in accepted_right_relations and x.text not in dates]
    punctuation_to_append_to_extract = [x for x in token.children if x.dep_ == 'punct' and
                   x.i == token.nbor().i and x.text not in dates
                   and x.text not in ['(']]
    punctuation_less_children = [x for x in token.children if x not in punctuation_to_append_to_extract]

    # Edge case prevention: relative clause as the only remaining valid option
    if (any(dep in ['relcl', 'prep', 'prt'] for dep in [x.dep_ for x in punctuation_less_children]) 
            and len(punctuation_less_children) <= 1):
        possible_paths = punctuation_less_children

    return get_first_elem_or_none(possible_paths)


# Given a token in a dependency tree, construct the context in which that
# token (most often being a 'DATE' named entity) was stated in the sentence.
def construct_context(token, dates):
    # Initialize the return object (dates check to remove redundant printing).
    extract = ''
    if token.text not in dates:
        extract = prepend_text_to_extract(token, extract, dates)
        extract += token.text

    # Note: .children, .lefts, and .rights return generators, not lists.
    children = list(token.children)
    initial_token = token
    stored_additional_iterations = []

    while not (list(children) == []):
        # Adds all the text in the right place to the extract.
        extract = add_punctuation_to_extract(token, extract, dates)
        extract = append_text_to_extract(token, extract, dates)
        # prevents reprinting of prepended text on initial loop
        if (token.text != initial_token.text):
            extract = prepend_text_to_extract(token, extract, dates)

        # Stores any additional iterations for later retrieval.
        split_branch = check_for_additional_iterations(token, dates)
        if split_branch:
            stored_additional_iterations = split_branch

        possible_paths = determine_next_word_to_navigate_to(token, dates)
        print_if_debug('\n\n')
        if possible_paths:
            # Reset the root/children to allow for indefinite iteration.
            token = possible_paths
            children = list(token.children)

            # Prevents redundant printing.
            if token.text not in dates:
                extract += ' ' + token.text
        else:
            children = []

        # If we've exhausted our options, we need to check if there's a valid
        # additional iteration to do.
        if children == [] and stored_additional_iterations:
            if stored_additional_iterations.text not in extract:

                # Reset the root/children to allow for indefinite iteration.
                token = stored_additional_iterations
                children = list(token.children)

                # Hard catch: prevents weird cases.
                if token.tag_ == 'VBG':
                    break

                # Prevents redundant printing.
                if token.text not in dates:
                    extract += ' ' + token.text

            # Reset the additional iteration to prevent infinite loops.
            stored_additional_iterations = []

    return extract


# Given a token (often a 'DATE' named entity), determine the highest possible
# navigation up the dep_tree that will return meaningful information. While a
# nlp sentence object has a .root function that gets the true root of the
# sentence, oftentimes the root of the sentence is too 'high up' on the tree.
def get_dep_tree_starting_point(token, dates):
    # note: need a better method to prevent the date
    # from appearing in its own context
    starting_token = token
    token_head = token.head

    if token_head.text in dates:
        return token
    while not (token.dep_ == 'ROOT'):
        if (token.i - 5 > token.head.i > token.i + 5 and
                token.dep_ not in ['prep', 'advcl']):
            return token
        # edge case: 'as' identifies somebody introducing their position,
        # which we prefer over their duties, while excluding terms such as
        # 'as of 2015'
        if (re.match(r'[a|A][s|t]', token.text) and
                'prep' not in [x.dep_ for x in token.children]):
            return token

        if [x for x in token.children if x.text == 'as']:
            return token

        # edge case: stem is the highest root element, and only has one child,
        # being the leaf element, and that head contains no usable data.
        # return the leaf
        children = [x for x in list(token_head.children) if not x.pos_ == 'PUNCT']
        if (len(children) == 1 and
                token_head.text == token_head.head.text and
                not (token_head.pos_ in ['NOUN', 'PROPN'])):
            if children[0].text == starting_token.text:
                return token

        # edge case: preventative measure of navigating too far up the tree
        # we want to return where we are currently
        if token_head.dep_ in ['nsubj', 'npadvmod', 'nsubjpass']:
            return token_head

        # edge case: navigating too far up the tree
        if token.dep_ == 'ccomp':
            return token

        # edge case: prevents retread of already supplied data
        if token_head.text in dates:
            return token

        # If all is good, move 'up' one level and continue going
        token = token_head
        token_head = token.head
    return token_head


# Given a text run through the nlp model, retrieve a dictionary consisting of
# each date and its context, tied to the sentence index it originates from.
# (Index needed for frontend display functionality).
def construct_dict_of_extracts(orig_doc_text, nlp_doc):
    # create a list of all the date entities tagged by the ner process
    dates = get_valid_dates(nlp_doc.ents)

    dates_and_their_contexts = []

    stored_sentence = None
    char_index = -1 * len(list(nlp_doc.sents)[0].text)
    sentence_index = -1
    sentence_has_valid_subject = True

    for token in nlp_doc:
        # If sentence changed, check if the sentences subject is valid
        # If it is not, skip over the sentence, as it refers to something the
        # applicant did not do themselves (eg a project's duration)
        if not token.sent == stored_sentence:
            char_index += len(token.sent.text)
            sentence_index += 1


        if not token.sent == stored_sentence and not len(token.sent) == len(nlp_doc):
            sentence_has_valid_subject = remove_bad_subjects(token.sent)

        if sentence_has_valid_subject:
            # If we're currently looking at a date's context
            if token.text in dates:
                # Get to the head of the dep_tree
                token_head = get_dep_tree_starting_point(token, dates)

                extract = strip_faulty_formatting(construct_context(token_head, dates))
                # Note: full sentence retrieved to minimize corruption caused by
                # differing word location in searched text
                match = fuzzy_search_extract_in_orig_doc(orig_doc_text, extract)
                if match:
                    dates_and_their_contexts.append((
                        (token.text + ": " + extract), match[0][0], match[1][1], sentence_index))
                else:
                    dates_and_their_contexts.append(((token.text + ": " + extract), 0, 0, sentence_index))
        stored_sentence = token.sent
    return dates_and_their_contexts


# Given a text block, finds any date entities and returns them, the context
# in which the date was stated, and the sentence index in the text where the
# date was extracted from.
def extract_when(original_text, doc):

    squash_named_entities(doc)
    doc = hard_identify_date_ents(doc)

    for ent in doc.ents:
        print_if_debug([(ent.text, ent.label_)])

    print_if_debug('\n\n')

    dates_and_contexts = construct_dict_of_extracts(original_text, doc)
    print_if_debug('\n\n')

    for extract_text, start, end, sent_i in dates_and_contexts:
        print_if_debug((extract_text, ' ~~~~~~~~~~~~ ', original_text[start:end], start, end, sent_i))
        print_if_debug('\n')

    return dates_and_contexts