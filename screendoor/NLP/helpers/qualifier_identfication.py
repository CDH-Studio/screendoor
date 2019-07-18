import re

#regex statements to filter out noise from date entities
months_regex = r'(?:\bjanuary\b|' \
               r'\bfebruary\b|' \
               r'\bmarch\b|' \
               r'\bapril\b|' \
               r'\bmay\b|' \
               r'\bjune\b|' \
               r'\bjuly\b|' \
               r'\baugust\b|' \
               r'\bseptember\b|' \
               r'\bnovember\b|' \
               r'\bdecember\b)'

present_day_regex = r'(?:present|today|current|now)'

linked_words = r'\band\b|\bto\b|\buntil\b'

special_words = r'(?:years|last|months|since)'

from dateutil.parser import *
from datetime import *
from .date_range import DateRange
from dateutil.relativedelta import *
from word2number import w2n

# Creates a list of DateRange objects. A date is only added to this list if
# it represents a direct range (July 2015 - August 2016) or an indirect range
# (Since 2011, last 4 years). Isolated dates (July 2015) are excluded.
def create_list_of_ranges(doc_ents, closing_date):
    date_range_list = []
    for ent in doc_ents:
        if 'DATE' in ent.label_:
            date_range = remove_noise_from_date(ent, closing_date)
            if date_range is not None:
                date_range_list.append(date_range)

    return date_range_list

# Removes noise from the date input to ensure that there are not any issues
# parsing dates of slight variations.
def remove_noise_from_date(raw_date, closing_date):
    # Conflates any linking words (to, until) to hyphens to standardize input
    text = re.sub(linked_words, '-', raw_date.text)

    cleaned_string = ''

    # edge case prevention
    if 'since' in raw_date.text.lower():
        cleaned_string = handle_edge_case_since(raw_date.text, closing_date)
    # edge case prevention
    elif 'last' in raw_date.text.lower():
        cleaned_string = handle_edge_case_last(raw_date.text, closing_date)
    else:
        # excludes any text not identified as meaningful
        regex = r'\d*|-|{0}|{1}|{2}'.format(months_regex, present_day_regex,
                                            special_words)
        split_date = re.split(r'[ ]+', text)
        for word in split_date:
            # check if the word isn't noise
            if [x for x in re.findall(regex, word.lower()) if x != ''] != []:
                #Handles cases like 'November 09' (meant as November 2009, not november 9th)
                if word.isdigit() and len(word) == 2:
                    if int(word) < 50:
                        word = '20' + word
                    else:
                        word = '19' + word

                cleaned_string += word + ' '

    return create_date_range(cleaned_string)


# Handles special case of dates formatted as 'since 2011', 'since July', etc.
# Assumes that they mean ~stated date~ to the present date (assumed as closing
# date of position, to make the parsing independant of when the screening is done)
def handle_edge_case_since(token, closing_date):
    text = re.sub(r'since|last', '', token.lower())

    if not re.findall(r'\d{4}', text.lower()):
        text += ' ' + str(closing_date.year)
    return text.strip() + '-present'


# Handles special case of dates formatted as 'last 4 months', 'last 2 years', etc.
# Assumes that they mean ~stated date~ relative to present date (assumed as closing
# date of position, to make the parsing independant of when the screening is done)
def handle_edge_case_last(token, closing_date):
    years= False
    if re.findall(r'years?', token.lower()):
        years = True
    quantifier = pull_number_from_date(token)

    if years:
        relative_date = closing_date + relativedelta(years=-quantifier)
    else:
        relative_date = closing_date + relativedelta(months=-quantifier)

    return relative_date.strftime('%Y %m') + '-present'


# Creates an instance of the DateRange class out of a string following the
# 'DATE' - 'DATE' format (where present-day is considered a valid date)
def create_date_range(cleaned_date):
    individual_dates = cleaned_date.split('-')
    date_list = []
    if len(individual_dates) > 1:
        for date in individual_dates:
            # Parses the date as either 'present' or the date listed
            if re.findall(present_day_regex, date.lower()):
                date = datetime.now()
            else:
                try:
                    date = parse(date.strip())
                except ValueError:
                    return None
            date_list.append(date)
    return DateRange(date_list)

# Given a list of date ranges, determine what date is the most recent.
# May be changed to include isolated dates?
def determine_most_recent_date(date_range_list):
    if date_range_list == []:
        return None

    # Default the most recent date to the first date found
    most_recent_date = date_range_list[0].get_date_upper()
    for index in range(1, len(date_range_list)):
        # Whenever a more recent date is found, set the most recent date to that
        diff = relativedelta(date_range_list[index].get_date_upper(), most_recent_date).years
        if diff >0:
            most_recent_date = date_range_list[index].get_date_upper()
    return most_recent_date

# Given a list of the applicant's experiences and the years/month threshold
# needed to pass the recency qualifer, determine if the applicant
# passed
def determine_if_recent_criteria_met(date_range_list, closing_date, recency_requirement, is_years):
    most_recent_experience = determine_most_recent_date(date_range_list)

    if is_years:
        cutoff_date = closing_date + relativedelta(years=-recency_requirement)
        if relativedelta(most_recent_experience, cutoff_date).years >= 0:
            return True
    else:
        cutoff_date = closing_date + relativedelta(months=-recency_requirement)
        if relativedelta(most_recent_experience, cutoff_date).months >= 0:
            return True

    return False

# Aggregate the experience an applicant has to a single value.
# Isolated dates excluded as their meaning is ambiguous.
def add_all_identified_ranges_together(date_range_list):
    if date_range_list == []:
        return None

    # works out to a blank constructor
    aggregate_range = relativedelta(0)

    for date_range in date_range_list:
        if date_range.get_date_range() is not None:
            aggregate_range += date_range.get_date_range()

    return aggregate_range


# Given a list of the applicant's experiences and the amount of years/months
# needed to pass the significance qualifer, determine if the applicant
# passed
def determine_if_significant_criteria_met(date_range_list, needed_quantity, is_years):
    total_experience = add_all_identified_ranges_together(date_range_list)
    if total_experience:
        if is_years:
            return True if total_experience.years >= needed_quantity else False
        else:
            return True if total_experience.months >= needed_quantity else False


# Given a number within a date, either stated verbosely (three, seven)
# or as a digit (3, 7), return it as an int.
def pull_number_from_date(text):
    identified_numbers = re.search(r'\d+', text)
    if identified_numbers:
        return int(re.search(r'\d+', text).group())
    else:
        try:
            return w2n.word_to_num(text)
        except ValueError:
            return 0

# Determine if a date refers to year threshold (at least 2 years) or a month
# threshold (within the last 8 months). In a perfect world, would throw an
# exception if neither is found (as the date means nothing)
def is_qualifying_years(date):
    if re.findall(r'years?', date.text.lower()):
        return True
    return False
