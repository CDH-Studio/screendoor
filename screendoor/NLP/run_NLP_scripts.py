from .when_extraction import extract_when
from .how_extraction import extract_how
from screendoor.models import NlpExtract
from screendoor_app.settings import NLP_MODEL
from .helpers.format_text import post_nlp_format_input


def generate_nlp_extracts(text, linked_answer):
    orig_doc = NLP_MODEL(text)
    reformatted_text = post_nlp_format_input(orig_doc)
    doc = NLP_MODEL(reformatted_text)

    dates_and_contexts = extract_when(orig_doc, doc)
    taken_sentence_indexes = []

    if dates_and_contexts != [] and dates_and_contexts is not None:
        save_nlp_extracts(dates_and_contexts, 'WHEN', linked_answer)
        taken_sentence_indexes = [x[3] for x in dates_and_contexts]

    experiences = extract_how(orig_doc, doc, taken_sentence_indexes)

    if experiences != [] and experiences is not None:
        save_nlp_extracts(experiences, 'HOW', linked_answer)

    print((linked_answer, text))

    for extract_text, start, end, sent_i in dates_and_contexts:
        print((extract_text, ' ~~~~~~~~~~~~ ', orig_doc.text[start:end], start, end, sent_i))
        print('\n')
    print('~~~~~~')
    for extract_text, start, end, sent_i in experiences:
        print((extract_text, ' ~~~~~~~~~~~~ ', orig_doc.text[start:end], start, end, sent_i))
        print('\n')


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