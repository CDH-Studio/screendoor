import re
from .general_helpers import print_if_debug

months_regex = r'\b(?:jan|feb|mar|apr|jun|jul|aug|sept|oct|nov|dec|' \
                    r'january|febuary|march|april|may|june|july|august|september|october|november|december)'
digits_or_present_regex = r'(?:\d*|present)'

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


# fix any false positives of dates being identified as other named entities
def hard_identify_date_ents(doc):
    # for now, only checks the 07/2015-05/2014 regex, but will be expanded
    # as needed
    regex = r'{0}\d*-{0}{1}'.format(months_regex, digits_or_present_regex)

    manually_identified_dates = re.findall(r"\d*\/\d*-\d*\/\d*", doc.text)
    manually_identified_dates += re.findall(regex, doc.text.lower())

    #creates a list of the dates' start/end positions in the doc
    identified_date_locations = []
    for date in manually_identified_dates:
        start = doc.text.lower().find(date)
        identified_date_locations.append((start, start + len(date)))


    recreated_named_entities = []

    # Adds the identified dates to the list of new entities
    for date_location in identified_date_locations:
        new_ent = doc.char_span(date_location[0], (date_location[1]),
                                label=u'DATEHACK')
        if not (new_ent is None):
            recreated_named_entities.append(new_ent)
        else:
            print_if_debug("ERROR: span not found. help")

    # Loops through the existing entities, leaving them out of the new list
    # if they are contained within the identified date entities
    # thus overriding any faulty NER done on dates
    for ent in doc.ents:
        start = doc.text.find(ent.text)
        end = start + len(ent.text)
        is_distinct = True

        for dates in identified_date_locations:
            if start >= dates[0] and end <= dates[1]:
                is_distinct = False
                break
        if is_distinct:
            recreated_named_entities.append(ent)

    doc.ents = recreated_named_entities
    return doc


# Overrides the date entity recognition, removing false positive dates
# Examples include "over the years", "months", "recently", and other dates
# That we can't extract meaningful information out of
def get_valid_dates(ents):
    dates = []
    for potential_date in [x for x in ents if 'DATE' in x.label_]:
        if not bool(re.search(r'[0-9]{4}|'
                              r'January|Febuary|March|April|May|June|'
                              r'July|August|September|November|December|'
                              r'Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Nov|Dec|'
                              r'last|ago', potential_date.text)):
            print_if_debug(('REMOVED DATE: ', potential_date.text))
            continue
        dates.append(potential_date.text)
    return dates
