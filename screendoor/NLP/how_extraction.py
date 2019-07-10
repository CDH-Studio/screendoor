from screendoor_app.settings import NLP_MODEL
from .helpers.general_helpers import remove_bad_subjects, get_first_elem_or_none, fuzzy_search_extract_in_orig_doc, print_if_debug, visualize_dep_tree_if_debugging
from .helpers.format_text import strip_faulty_formatting, post_nlp_format_input
from .helpers.how_extraction_helpers import create_phrase

def construct_how_extract(sent):
    # Filter out sentences without valid subjects.
    if not remove_bad_subjects(sent):
        return None

    # Span objects do not care about sentence boundaries, so a new doc is
    # created off the sentence to stop any boundary crossing in the looping.
    doc = sent.as_doc()

    # Find all the verbs.
    verbs = [x for x in doc if x.pos_ == 'VERB' and not x.dep_ == 'amod']
    if verbs == []:
        return None

    # Pull out two types of verbs from the verb list: sentence roots, or
    # relative clause modifiers.
    root = get_first_elem_or_none([x for x in verbs if x.dep_ == 'ROOT'])
    relcl = get_first_elem_or_none([x for x in verbs if x.dep_ == 'relcl'])
    amod = get_first_elem_or_none([x for x in verbs if x.dep_ == 'amod'])

    extract = ''

    phrase = create_phrase(doc, root, relcl, amod)

    # If no valid verb phrase was found, skip.
    if not phrase:
        return None

    for idx, token in enumerate(phrase):

        # Attempts to "atomize" the verb phrase, by removing unneeded details,
        # or other ideas being explored in the same sentence
        if token.text == ';':
            extract += '--'
            break
        if token.text == ',' and idx < len(phrase)-1:
            if 'conj' not in [x.dep_ for x in token.head.children] \
                    or token.nbor().dep_ == 'appos':
                extract+= '--'
                break

        extract += ' ' + token.text
    return extract


# Given a text block, finds any actions or duties an applicant mentioned,
# in the case where the applicant is directly referring to themselves.
# (e.g. I acquired x  VS  the project acquired x)
def extract_how(text, taken_sentence_indexes):
    orig_doc = NLP_MODEL(text)
    reformatted_text = post_nlp_format_input(orig_doc)
    doc = NLP_MODEL(reformatted_text)

    experiences = []
    matches = []
    for idx, sent in enumerate(doc.sents):
        if idx not in taken_sentence_indexes:
            experience = strip_faulty_formatting(construct_how_extract(sent))
            if experience:
                # retrieve the location of the extract in the original formatted
                # text (for display purposes)
                match = fuzzy_search_extract_in_orig_doc(orig_doc.text, experience, matches)
                if match:
                    experiences.append((experience, match[0][0], match[0][1], idx))
                    matches.append(match[1])
                else:
                    # Should never get here!
                    experiences.append((experience, -1, -1, idx))
    print_if_debug('\n')

    for extract_text, start, end, sent_i in experiences:
        print_if_debug((extract_text, ' ~~~~~~~~~~~~ ', orig_doc.text[start:end], start, end, sent_i))
        print_if_debug('\n')

    if experiences == []:
        print_if_debug("NO EXTRACTION FOUND")
    for x in doc.sents:
        print_if_debug(repr(x).replace('\n', '/N'))
        print_if_debug("~x~x~x~x~x~x~x~x~x~x~x~x~x~x~x~x~")

    visualize_dep_tree_if_debugging(doc)

    return experiences