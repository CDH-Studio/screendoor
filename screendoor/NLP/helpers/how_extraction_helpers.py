# Makes sure information such as "have worked" isn't lost
def grab_verb_phrase(doc, i):
    if i > 0:
        if doc[i-1].dep_ == 'aux':
            return doc[i-1:]
    return doc[i:]


# Checks the subject tied directly to the verb (nouns not included)
def is_valid_subject(verb):
    if 'nsubj' in [x.dep_ for x in verb.children if not x.pos_ == 'NOUN']:
        return True
    return False


# Hierarchy: If there is a verb acting as the root, take it, else take the
# first available relative clause instead. If neither, return none (as no
# valid verb has been found)
def create_phrase(doc, root, relcl):
    phrase = None
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

    return phrase