from .when_extraction import extract_when
from .how_extraction import extract_how
from screendoor.models import NlpExtract, Qualifier
from screendoor_app.settings import NLP_MODEL
from .helpers.format_text import post_nlp_format_input, strip_faulty_formatting, replace_acronyms_with_full_month, clear_clarification
from .helpers.qualifier_identfication import create_list_of_ranges, \
    pull_number_from_date, is_qualifying_years, \
    determine_if_recent_criteria_met, determine_if_significant_criteria_met
import re

# Runs both the when_extraction and how_extraction (in that order, as the how
# extraction depends on the date extractions (to not overlap)
def generate_nlp_extracts(comp_response_text, linked_question, linked_answer, closing_date):
    # Create the NLP doc objects of both the originally formatted text,
    # and the secret reformatted text
    orig_doc = NLP_MODEL(comp_response_text)

    reformatted_text = post_nlp_format_input(orig_doc)
    reformatted_text = replace_acronyms_with_full_month(strip_faulty_formatting(reformatted_text))
    doc = NLP_MODEL(reformatted_text)

    # replace with position closing date!
    date_ranges = create_list_of_ranges(doc.ents, closing_date)

    if linked_question is not None:
        analyze_question_qualifiers(linked_question.question_text, date_ranges, closing_date, linked_answer)

    dates_and_contexts = extract_when(orig_doc.text, doc)

    taken_sentence_indexes = []
    if dates_and_contexts != [] and dates_and_contexts is not None:
        save_nlp_extracts(dates_and_contexts, 'WHEN', linked_answer)
        taken_sentence_indexes = [x[3] for x in dates_and_contexts]

    experiences = extract_how(orig_doc.text, doc, taken_sentence_indexes)

    if experiences != [] and experiences is not None:
        save_nlp_extracts(experiences, 'HOW', linked_answer)


# takes in the question text, and determines whether the supplied date ranges
# meet (or exceed) the stated requirements (if any) of the question.
# Only checks requirements with a date threshold (significance) or with a
# timeframe (recency)
def analyze_question_qualifiers(question_text, date_ranges, closing_date, answer):
    # Run the question text through the NLP, and pull out the dates
    formatted_question_text = clear_clarification(question_text)
    nlp_question_text = NLP_MODEL(formatted_question_text)

    for sentence in nlp_question_text.sents:
        for date in [x for x in sentence.ents if 'DATE' in x.label_]:
            quantifier = pull_number_from_date(date.text)
            is_years = is_qualifying_years(date)

            if re.search(r'least|over|more|approximately', date.text):
                qualifier_type = 'SIGNIFICANCE'

                status = determine_if_significant_criteria_met(date_ranges, quantifier,
                                                      is_years)
            elif re.search(r'within|last', date.text):
                qualifier_type = 'RECENCY'
                status = determine_if_recent_criteria_met(date_ranges, closing_date,
                                                 quantifier, is_years)
            else:
                return

            if status is None:
                status = False
            save_qualifier(sentence, qualifier_type, status, answer)


def save_nlp_extracts(extract_list, nlp_type, answer):
    extracts = []
    for extract_data in extract_list:
        extract = NlpExtract(parent_answer=answer, extract_type=nlp_type,
                             extract_text=extract_data[0],
                             extract_sentence_index=extract_data[1],
                             extract_ending_index=extract_data[2])
        extract.save()
        extracts.append(extract)
    extract_set = NlpExtract.objects.filter(parent_answer=answer).order_by(
        'extract_sentence_index', '-extract_type')
    counter = 0
    while counter < len(extract_set) - 1:
        counter += 1
        extract_set[counter -
                    1].next_extract_index = extract_set[counter].extract_sentence_index
    for e in extract_set:
        e.save()


def save_qualifier(qualifier_text, qualifier_type, status, answer):
    qualifier = Qualifier(parent_answer=answer, qualifier_text=qualifier_text,
                          qualifier_type=qualifier_type, status=status)
    qualifier.save()