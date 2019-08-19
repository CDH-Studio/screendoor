import re
from spacy import displacy
from fuzzysearch import find_near_matches

# IMPORTANT NOTE: DISABLE THESE FOR PRODUCTION, ONLY FOR DEBUGGING
DEBUG = False
DISPLACY = False
def print_if_debug(text):
    if DEBUG:
        print('~-+ ', text)


# Attempts to filter out any bad subjects (note: absence of a subject assumes
# the applicant is referring to themselves).
def remove_bad_subjects(sent):
    # If a sentence fragment is verbless, it is most often a list heading.
    verbs = [x for x in sent if x.pos_ == 'VERB']
    if not verbs:
        #print_if_debug(('INCLUDED-WHEN EXCLUDED-HOW verbless', sent))
        return True

    identified_subjects = [x for x in sent if x.dep_ == 'nsubj' or x.dep_ == 'nsubjpass' and not x.pos_ == 'VERB']

    # If no subject is found, it is assumed to be a bullet point (and thus valid)
    if identified_subjects == []:
        #print_if_debug(('INCLUDED subject-less', sent))
        return True
    else:

        # Checks for both I (I worked on...) and 'as' (as a team lead, i worked on...)
        primary_check = [item for sublist in [re.findall(r'\bI\b|\b[a|A]s\b', x.text) for x in identified_subjects] for item in sublist]

        # Checks for specific phrases that are neeced
        secondary_check = [item for sublist in [re.findall(r'\b[m|M]y responsibilities|[m|M]y tasks\b', x.text) for x in identified_subjects] for item in sublist]
        
        subject_an_org = not set([x.text for x in identified_subjects]).isdisjoint([x.text for x in sent.ents if x.label_ == 'ORG'])

        if not (primary_check + secondary_check == []) or subject_an_org:
            #print_if_debug(('INCLUDED Applicant subject', identified_subjects, sent))
            return True

    #print_if_debug(('EXCLUDED subject', identified_subjects, sent))
    return False


# Given an element at i, get the element at i+1 if it doesn't cause an index
# out of bounds error. returns blank rather than none as its main usage is
# in the newline reformatting, where a blank line is also ''.
def get_next_index_or_blank(idx, list):
    if idx < len(list)-1:
        return list[idx+1]
    return ''

# Given a list, return the first element, or none if the list is blank.
# Less verbose than the inline if statement equivalent.
def get_first_elem_or_none(list):
    if not list == []:
        return list[0]
    return None

# For local development, calls displacy to render a visualization of the dep tree.
# Does not like docker, and will hang the program if called inside the container.
def visualize_dep_tree_if_debugging(doc):
    if DISPLACY:
        sentence_spans = list(doc.sents)
        # show dependency tree (http://localhost:5000/)
        options = {'color': 'red', 'compact': True,  #'fine_grained':True,
                   'collapse_punct': False, 'distance': 350}
        displacy.serve(sentence_spans, style='dep', options=options)


# Returns the location of the found extract in the original document
def fuzzy_search_extract_in_orig_doc(original_doc_text, searched_text, stored_matches):
    # Note; scripts return blanks instead of null values
    if searched_text != '':
        matches = []
        threshold = 1
        while matches == [] and threshold < 10:
            threshold += 2
            matches = find_near_matches(searched_text, original_doc_text, max_l_dist=threshold)

        match = get_first_elem_or_none(matches)
        if len(matches) == 1:
            return ((match[0], match[1]), match)
        while match:
            if not check_if_stored_already(match, stored_matches):
                print_if_debug(("MATCH FOUND: ", original_doc_text[match[0]:match[1]], threshold))
                matches += match
                return ((match[0], match[1]), match)
            matches = matches[1:len(matches)]
            match = get_first_elem_or_none(matches)

    return None


def check_if_stored_already(match_to_test, matches):
    for match in matches:
        #checks if the bounds are within another match
        if match_to_test[0] >= match[0] and match_to_test[0] <= match[1]:
            return True
    return False
