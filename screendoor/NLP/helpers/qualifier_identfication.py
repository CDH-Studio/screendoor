import re

from dateutil.parser import *
from datetime import *
from .date_range import DateRange
from dateutil.relativedelta import *
from word2number import w2n
from .when_extraction_helpers import get_valid_dates

# regex statements to filter out noise from date entities
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


# Creates a list of DateRange objects. A date is only added to this list if
# it represents a direct range (July 2015 - August 2016) or an indirect range
# (Since 2011, last 4 years). Isolated dates (July 2015) are excluded.
def create_list_of_ranges(doc_ents, closing_date):
    date_range_list = []
    for ent in get_valid_dates(doc_ents):
        date_range = remove_noise_from_date(ent, closing_date)
        if date_range is not None:
            date_range_list.append(date_range)
    return date_range_list


# Removes noise from the date input to ensure that there are not any issues
# parsing dates of slight variations.
def remove_noise_from_date(raw_date, closing_date):
    # Conflates any linking words (to, until) to hyphens to standardize input
    text = re.sub(linked_words, '-', raw_date)

    cleaned_string = ''

    # edge case prevention
    if 'since' in raw_date.lower():
        cleaned_string = handle_edge_case_since(raw_date, closing_date)
    # edge case prevention
    elif 'last' in raw_date.lower():
        cleaned_string = handle_edge_case_last(raw_date, closing_date)
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

    return create_date_range(cleaned_string, closing_date)


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
    return relative_date.strftime('%Y %m %d') + '-present'


# When a user simply states an ambiguous date (such as July 2015, 2013, etc),
# the missing months/days are taken as today's values (e.g. assuming today is
# August 1st, the above would become July 1st 2015, August 1st 2013). This is
# to ensure that the internal date delta logic is consistent with expectations
# (as 2013 alone is too ambiguous for any calculations). This function corrects
# that logic to take the closing date of the position, rather than the current
# date, so that the parsing is guaranteed to return the same result every time,
# regardless of the date of the application processing.
def correct_ambiguity_to_closing_date(date_string, date, closing_date):
    month_replace = date.month
    months = re.findall(months_regex, date_string.lower())
    if months == []:
        month_replace = closing_date.month

    days_replace = date.day
    days = re.findall(r'\b\d{1}\b|\b\d{2}\b', date_string.lower())
    if days == []:
        days_replace = closing_date.day
    return date.replace(month=month_replace, day=days_replace)


# Creates an instance of the DateRange class out of a string following the
# 'DATE' - 'DATE' format (where present-day is considered a valid date)
def create_date_range(cleaned_date, closing_date):
    individual_dates = cleaned_date.split('-')
    date_list = []
    if len(individual_dates) > 1:
        for date_string in individual_dates:
            # Parses the date as either 'present' or the date listed
            if re.findall(present_day_regex, date_string.lower()):
                date_object = datetime.now()
            else:
                try:
                    date_object = parse(date_string.strip())
                except ValueError:
                    return None
            date_object = correct_ambiguity_to_closing_date(date_string.strip(), date_object, closing_date)
            date_list.append(date_object)

        return DateRange(date_list[0:2])
    return None


# Remove any redundant date ranges (e.g. 2012-2013 and 2012-2014), which is
# needed to ensure the significance identification works properly (for the
# above example, the aggregate should be 2 years of experience (2012-2014).
def remove_overlapping_ranges(date_range_list):
    if date_range_list == []:
        return date_range_list

    new_date_ranges = []
    print (date_range_list)
    date_range_list.sort()
    new_date_ranges.append(date_range_list[0])

    for index in range(1, len(date_range_list)):
        if is_delta_positive(relativedelta(new_date_ranges[-1].get_date_upper(), date_range_list[index].get_date_lower())):
            combined_range = combine_date_ranges(new_date_ranges[-1], date_range_list[index])
            new_date_ranges[-1] = combined_range
        else:
            new_date_ranges.append(date_range_list[index])

    return new_date_ranges


# Given two date ranges, return one that takes the lowest of the two's lower
# date, and the higher of the two's upper date (e.g. 2013-2015 and 2012-2014
# returns 2012-2015)
def combine_date_ranges(date_range_one, date_range_two):

    date_lower = date_range_one.get_date_lower() if \
        date_range_one.get_date_lower() < date_range_two.get_date_lower() \
        else date_range_two.get_date_lower()

    date_upper = date_range_one.get_date_upper() if \
        date_range_one.get_date_upper() > date_range_two.get_date_upper() \
        else date_range_two.get_date_upper()

    return DateRange([date_lower, date_upper])

def is_delta_positive(delta):
    if delta.days > 0 or delta.months > 0 or delta.years > 0:
        return True
    return False


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
    # if most_recent_experience is None:
    #     return False

    if is_years:
        cutoff_date = closing_date + relativedelta(years=-recency_requirement)
        if relativedelta(most_recent_experience, cutoff_date).years >= 0:
            return 'Passed'
    else:
        cutoff_date = closing_date + relativedelta(months=-recency_requirement)
        if relativedelta(most_recent_experience, cutoff_date).months >= 0:
            return 'Passed'

    return 'Failed'


# Aggregate the experience an applicant has to a single value.
# Isolated dates excluded as their meaning is ambiguous.
def add_all_identified_ranges_together(date_range_list):
    if date_range_list == []:
        return None
    date_range_list = remove_overlapping_ranges(date_range_list)
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
    date_range_list = remove_overlapping_ranges(date_range_list)
    total_experience = add_all_identified_ranges_together(date_range_list)

    if total_experience:
        if is_years:
            return 'Passed' if total_experience.years >= needed_quantity else 'Failed'
        else:
            return 'Passed' if total_experience.months >= needed_quantity else 'Failed'


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