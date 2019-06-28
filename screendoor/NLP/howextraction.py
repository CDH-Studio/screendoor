from screendoor_app.settings import NLP_MODEL
from .NLPhelperfunctions import format_text, clean_output, remove_bad_subjects

# Checks the subject tied directly to the verb.
def is_valid_subject(verb):
    if 'nsubj' in [x.dep_ for x in verb.children if not x.pos_ == 'NOUN']:
        return True
    return False


def get_first_elem_or_none(list):
    if not list == []:
        return list[0]
    return None

# Makes sure information such as "have worked" isn't lost.
def grab_verb_phrase(doc, i):
    if i > 0:
        if doc[i-1].dep_ == 'aux':
            return doc[i-1:]
    return doc[i:]

def iterate_through_dep_tree(sent):
    # Filter out sentences without valid subjects.
    if not remove_bad_subjects(sent):
        return None

    # Span objects do not care about sentence boundaries, so a new doc is
    # created off the sentence to stop any boundary crossing in the looping.
    doc = sent.as_doc()

    # Find all the verbs.
    verbs = [x for x in doc if x.pos_ == 'VERB']

    # Pull out two types of verbs from the verb list: sentence roots, or
    # relative clause modifiers.
    root = get_first_elem_or_none([x for x in verbs if x.dep_ == 'ROOT'])
    relcl = get_first_elem_or_none([x for x in verbs if x.dep_ == 'relcl'])

    phrase = None
    context = ''

    # Hierarchy: If there is a verb acting as the root, take it, else take the
    # first available relative clause instead.
    if root:
        if is_valid_subject(root):
            phrase = grab_verb_phrase(doc, root.i)
        else:
            return None
    elif relcl:
        if is_valid_subject(relcl):
            phrase = grab_verb_phrase(doc, relcl.i)
        else:
            return None

    # If no valid verb phrase was found, skip.
    if not phrase:
        return None

    for token in phrase:

        # Attempts to "atomize" the verb phrase, by removing unneeded details,
        # or other ideas being explored in the same sentence.
        if token.text == ',':
            if 'conj' not in [x.dep_ for x in token.head.children] \
                    or token.nbor().dep_ == 'appos':
                context+= '---'
                break

        context += ' ' + token.text
    return context


def extract_how(text):
    doc = NLP_MODEL(format_text(text))

    experience_list = {}
    for idx, sent in enumerate(doc.sents):
        experience = clean_output(iterate_through_dep_tree(sent))
        if experience:
            experience_list[experience] = idx

    return experience_list
