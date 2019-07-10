from .when_extraction_helpers import get_valid_dates
from .general_helpers import get_next_index_or_blank, print_if_debug
import re

# Secretly adds periods to the input to make it parseable by the nlp script
# NOTE: needs to be done post nlp processing, as we need certain aspects of
# the nlp parsing to make the formatting more intelligent and context sensitive
# e.g. finding dates as list headings.
# Returns a nlp model, meaning long answers that take a long time to parse
# may impede overall performance. No way around this.
def post_nlp_format_input(nlp_parsed_text):
    dates = get_valid_dates(nlp_parsed_text.ents)
    a_bullet_point_char = (('.', '-', 'o', '&#61656;', '&#61607;'))
    reformatted_text = ''
    # Note: a sentence is broken by sentence boundary characters (. ! ?)
    for sentence in nlp_parsed_text.sents:
        newline_split_sentence = sentence.text.split('\n')

        # A sentence fragment is something that may or may not need to be
        # 'converted' into a full sentence, depending on the context of the
        # surronding information.
        for idx, sentence_fragment in enumerate(newline_split_sentence):
            sentence_fragment = sentence_fragment.strip()
            next_sentence_fragment = get_next_index_or_blank(idx, newline_split_sentence).strip()
            # Prevents bad data caused by people using periods as bullet points.
            if sentence_fragment in ['.', '']:
                continue

            if sentence_fragment.endswith(('...')):
                sentence_fragment = sentence_fragment[
                                    0:len(sentence_fragment) - 3]
            # If the element introduces a bullet point list (colons are not considered
            # sentence boundaries).
            if sentence_fragment.endswith((':', ';')):
                sentence_fragment = sentence_fragment[0:len(sentence_fragment)-1]

            # If the element ends with a valid boundary, it's already a sentence.
            if not sentence_fragment.endswith('.'):

                # If a double new line is detected.
                if next_sentence_fragment == '':
                    sentence_fragment = sentence_fragment+ '.'
                # If the current element has a date and no verb (considered a 'list heading').
                elif any(substring in sentence_fragment for substring in dates):
                    sentence_fragment = sentence_fragment + '.'
                # If the next element is a bullet point.
                elif next_sentence_fragment.startswith(a_bullet_point_char):
                    sentence_fragment = sentence_fragment + '.'

                # Note: new line characters are meaningless to the parser, so there
                # is no reason to maintain them in the input.
            if not sentence_fragment.endswith('.'):
                reformatted_text += remove_starting_bullet_point_chars(sentence_fragment) + '; '
            else:
                reformatted_text += remove_starting_bullet_point_chars(
                    sentence_fragment) + ' '
    print_if_debug(reformatted_text)
    return reformatted_text


# Takes a block of line breaks, and attempts to cut out the pdf-imposed style
# line breaks, leaving only the line breaks the applicants added.
def reprocess_line_breaks(text_block):
    a_bullet_point_char = (('.', '-', 'o', '&#61656;', '&#61607;'))
    if text_block is not None:
        line_split_blocks = text_block.split('\n')
        reprocessed_blocks = []
        reformatted_text = ''
        for idx, text in enumerate(line_split_blocks):
            next_elem = get_next_index_or_blank(idx, line_split_blocks)

            reformatted_text += text + ' '
            # Checks for: double or higher consecutive newlines (needed as
            # page breaks on the pdf can result in up to 7 line breaks.
            if text in ['', ' '] and next_elem in ['', ' ']:
                reformatted_text = ''
                continue

            # Checks for: line length being too short and not being in the
            # middle of a sentence, a blank line being read in, a sentence
            # end followed by a blank line, and the next element being a bullet
            # point character
            if ((len(text) < 115)
                    or text in ['', ' ']
                    or next_elem in ['', ' ']
                    or next_elem.strip().startswith(a_bullet_point_char)
                    and not re.match(r'[a-z]', next_elem.strip())):
                reprocessed_blocks.append(reformatted_text)
                reformatted_text = ''
                continue
        print_if_debug(reprocessed_blocks)
        return ('\n'.join(reprocessed_blocks)).strip(' \n')
    return None


def remove_starting_bullet_point_chars(text):
    # remove any leading spaces/tabs so the startswith doesnt need to check for variations
    text = text.strip()

    # 1 letter bullet points
    if text.startswith(('.', '-', 'o')):
        text = text[1:len(text)]
    # 8 letter bullet points (unescaped unicode bullet point chars)
    elif text.startswith(('&#61656;', '&#61607;')):
        text = text[8:len(text)]

    return text.strip()


# Remove faulty spacing, hanging punctuation, and other formatting issues
# so the return value displays all nice
def strip_faulty_formatting(text):
    if text == None:
        return None
    text = text.strip()
    if text.endswith('('):
        text = text[0:len(text) - 1]
    if text.endswith(' :') or text.endswith(' ;') or text.endswith(' ,'):
        text = text[0:len(text) - 2]
    if text.startswith(' '):
         text = text[1:len(text)]
    text = text.replace('( ', '(')
    text = text.replace(' )', ')')
    text = text.replace(" '", "'")
    text = text.replace(" , ", ", ")
    text = text.replace(" - ", "-")
    text = text.replace(" .", ".")
    text = text.replace("..", ".")
    text = text.replace('\t', ' ')
    text = text.replace('  ', ' ')
    text = text.replace(' ; ', ' ')
    if text.count('(') > text.count(')'):
        text += ')'
    return text