from screendoor_app.settings import NLP_MODEL
from .helpers.general_helpers import remove_bad_subjects, get_first_elem_or_none, print_if_debug, fuzzy_search_extract_in_orig_doc
from .helpers.format_text import post_nlp_format_input, strip_faulty_formatting
from .helpers.when_extraction_helpers import squash_named_entities, get_valid_dates, hard_identify_date_ents
from .helpers.extract_indices import ExtractIndices
import re

# relations that contain supplementary information we want, but not as the
# path we want to create. Mostly for content like "and" and "to".
prepend_relations = ['aux', 'auxpass', 'nsubj', 'nsubjpass', 'mark',
                     'advmod', 'amod', 'compound', 'poss', 'nmod',
                     'compound', 'neg', 'quantmod', 'nummod']

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


# Searches for any 'split branches', to avoid dead-ending dep_tree navigation when
# valuable information remains to be processed.
def check_for_additional_iterations(token, dates):
    words_for_additional_iteration = [x for x in token.rights if
                                      x.dep_ in additional_iteration_relations and
                                      not x.i > token.i + 7]

    return get_first_elem_or_none(words_for_additional_iteration)


# Searches for tokens that are determined to be valid iteration paths for
# dep_tree navigation.
def determine_next_word_to_navigate_to(token, dates):
    possible_paths = [x for x in token.lefts if
                      x.dep_ in accepted_left_relations  and token.i - x.i < 5] + \
                     [x for x in token.rights if
                      x.dep_ in accepted_right_relations]
    punctuation_to_append_to_extract = [x for x in token.children if x.dep_ == 'punct' and
                   x.i == token.nbor().i 
                   and x.text not in ['(']]
    punctuation_less_children = [x for x in token.children if x not in punctuation_to_append_to_extract]
    # Edge case prevention: awkward deps as the only remaining valid option
    if (any(dep in ['relcl', 'prep', 'prt'] for dep in [x.dep_ for x in punctuation_less_children]) 
            and len(punctuation_less_children) <= 1):
        possible_paths = punctuation_less_children

    return get_first_elem_or_none(possible_paths)


# Given a token, retrieve the logical context stemming from that element
# via an object that represents its index in the nlp document its from.
def construct_extract_indices(token, dates):
    # Construct the Indices object, exlcuding the starting date element.
    if token.text not in dates:
        extract = ExtractIndices(token.i)
    else:
        extract = ExtractIndices(token.i+1)

    # Note: .children, .lefts, and .rights return generators, not lists.
    children = list(token.children)
    stored_additional_iterations = []

    while not (list(children) == []):
        # Add prepend-relations to extract.
        extract.update_indices_with_list([x.i for x in token.lefts if
                                          x.dep_ in prepend_relations and
                                          not x.tag_ == 'XX' and
                                          x.text not in dates and
                                          token.text not in dates])

        # Add append-relations to extract.
        extract.update_indices_with_list([x.i for x in token.children if
                                          x.dep_ in append_relations and
                                          x == token.nbor() and
                                          x.text not in dates and
                                          token.text not in dates])

        # Add punctuation to extract.
        extract.update_indices_with_list([x.i for x in token.children if
                                          x.dep_ == 'punct' and
                                          x.i == token.nbor().i and
                                          x.text not in dates and
                                          token.text not in dates])

        # Stores any additional iterations for later retrieval.
        split_branch = check_for_additional_iterations(token, dates)
        if split_branch:
            stored_additional_iterations = split_branch

        # Finds any valid paths for iterations.
        possible_paths = determine_next_word_to_navigate_to(token, dates)
        if possible_paths:
            # Reset the root/children to allow for indefinite iteration.
            token = possible_paths
            children = list(token.children)

            if token.text not in dates:
                    extract.update_indices_with_index(token.i)
        else:
            children = []

        # If options exhausted, need to check if there's a valid
        # additional iteration to do.
        if children == [] and stored_additional_iterations:
            if extract.does_not_contain(stored_additional_iterations.i):

                # Reset the root/children to allow for indefinite iteration.
                token = stored_additional_iterations
                children = list(token.children)

                # Hard catch: prevents weird cases.
                if token.tag_ == 'VBG':
                    break

                if token.text not in dates:
                    extract.update_indices_with_index(token.i)

            # Reset the additional iteration to prevent infinite loops.
            stored_additional_iterations = []

    # Ensures a token isn't cut off.
    extract.update_indices_with_index(token.i+1)
    return extract


# Given a token (often a 'DATE' named entity), determine the highest possible
# navigation up the dep_tree that will return meaningful information. While a
# nlp sentence object has a .root function that gets the true root of the
# sentence, oftentimes the root of the sentence is too 'high up' on the tree.
def get_dep_tree_starting_point(token, dates):
    # note: need a better method to prevent the date
    # from appearing in its own context.
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
        # 'as of 2015'.
        if (re.match(r'[a|A][s|t]', token.text) and
                'prep' not in [x.dep_ for x in token.children]):
            return token

        if [x for x in token.children if x.text == 'as']:
            return token

        # edge case: stem is the highest root element, and only has one child,
        # being the leaf element, and that head contains no usable data;
        # return the leaf.
        children = [x for x in list(token_head.children) if not x.pos_ == 'PUNCT']
        if (len(children) == 1 and
                token_head.text == token_head.head.text and
                not (token_head.pos_ in ['NOUN', 'PROPN'])):
            if children[0].text == starting_token.text:
                return token

        # edge case: preventative measure of navigating too far up the tree;
        # we want to return where we are currently.
        if token_head.dep_ in ['nsubj', 'npadvmod', 'nsubjpass']:
            return token_head

        # edge case: navigating too far up the tree.
        if token.dep_ == 'ccomp':
            return token

        # edge case: prevents retread of already supplied data.
        if token_head.text in dates:
            return token

        # If all is good, move 'up' one level and continue going.
        token = token_head
        token_head = token.head
    return token_head


# Given a text run through the nlp model, retrieve a dictionary consisting of
# each date and its context, tied to the sentence index it originates from.
# (Index needed for frontend display functionality).
def construct_date_and_context(orig_doc_text, nlp_doc):
    # create a list of all the date entities tagged by the ner process.
    dates = get_valid_dates(nlp_doc.ents)

    dates_and_their_contexts = []

    stored_sentence = None
    char_index = -1 * len(list(nlp_doc.sents)[0].text)
    sentence_index = -1
    sentence_has_valid_subject = True
    matches = []

    for token in nlp_doc:
        # If sentence changed, check if the sentences subject is valid
        # If it is not, skip over the sentence, as it refers to something the
        # applicant did not do themselves (eg a project's duration).
        if not token.sent == stored_sentence:
            char_index += len(token.sent.text)
            sentence_index += 1

        if (not token.sent == stored_sentence and
                not len(token.sent) == len(nlp_doc)):
            sentence_has_valid_subject = remove_bad_subjects(token.sent)

        if sentence_has_valid_subject:
            # If we're currently looking at a date's context
            if token.text in dates:
                # Get to the head of the dep_tree
                token_head = get_dep_tree_starting_point(token, dates)

                # Get the lower/upper bound of the extract's location
                indices = construct_extract_indices(token_head, dates)

                # Retrieve the extract in the reprocessed doc, and format it
                # to look correct
                extract = nlp_doc[
                    indices.get_lower_bound():
                    indices.get_upper_bound()].text

                # Find the extract's location in the original doc
                match = fuzzy_search_extract_in_orig_doc(
                    orig_doc_text, extract, matches)

                if match:
                    dates_and_their_contexts.append((
                        (token.text + ": " + extract), match[0][0], match[1][1], sentence_index))
                    matches.append(match[1])
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

    dates_and_contexts = construct_date_and_context(original_text, doc)
    print_if_debug('\n\n')

    for extract_text, start, end, sent_i in dates_and_contexts:
        print_if_debug((extract_text, ' ~~~~~~~~~~~~ ', original_text[start:end], start, end, sent_i))
        print_if_debug('\n')

    return dates_and_contexts
