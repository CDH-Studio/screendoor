import os
import random
import string

import pandas as pd
import tabula
from pandas import options

from screendoor.models import Applicant
from screendoor.uservisibletext import ErrorMessages


def text_between(start_string, end_string, text):
    # Effectively returns the string between the first occurrence of start_string and end_string in text
    extracted_text = text.split(start_string, 1)[1].split(end_string, 1)[0]

    return extracted_text


def parse_citizenship(item):
    table = item[[0, 1]]
    applicant_citizenship = table.loc[(table[0] == "Citoyenneté / Citizenship:").idxmax(), 1]
    if "Canadian Citizen" in applicant_citizenship:
        applicant_citizenship = "Canadian Citizen"
    print("citizenship: " + applicant_citizenship)
    return applicant_citizenship


def parse_priority(item):
    table = item[[0, 1]]
    applicant_has_priority = \
        table.loc[(table[0] == "Droit de priorité / Priority entitlement:").idxmax(), 1]
    if "No" in applicant_has_priority:
        applicant_has_priority = "False"
    else:
        applicant_has_priority = "True"
    print("Priority: " + applicant_has_priority)
    return applicant_has_priority


def parse_is_veteran(item):
    table = item[[0, 1]]
    applicant_is_veteran = table.loc[
        (table[0] == "Préférence aux anciens combattants / Preference to veterans:").idxmax(), 1]
    if "No" in applicant_is_veteran:
        applicant_has_priority = "False"
    else:
        applicant_has_priority = "True"
    print("Veteran?: " + applicant_is_veteran)
    return applicant_is_veteran


def parse_first_official_language(item):
    table = item[[0, 1]]
    first_official_language = \
        table.loc[(table[0] == "Première langue officielle / First official language:").idxmax(), 1]
    applicant_first_official_language = first_official_language.split(" / ")[1]
    print("First Official Language: " + applicant_first_official_language)
    return applicant_first_official_language


def parse_working_ability(item):
    table = item[[0, 1]]
    working_ability = table.loc[(table[0] == "Connaissance pratique / Working ability:").idxmax(), 1]
    return working_ability


def parse_english_ability(working_ability):
    english_working_ability = working_ability.split("Anglais / English:", 1)[1].split(" / ")[1]
    print("English Ability: " + english_working_ability)

    return english_working_ability


def parse_french_ability(working_ability):
    french_working_ability = \
        text_between("Français / French :", "Anglais / English:", working_ability).split(" / ")[1]
    print("French Ability: " + french_working_ability)
    return french_working_ability


def parse_written_exam_language(item):
    table = item[[0, 1]]
    written_exam_language = table.loc[(table[0] == "Examen écrit / Written exam:").idxmax(), 1]
    applicant_written_exam_language = written_exam_language.split(" / ")[1]
    print("Written Exam Language: " + applicant_written_exam_language)
    return applicant_written_exam_language


def parse_corresponsence_language(item):
    table = item[[0, 1]]
    correspondence_language = table.loc[(table[0] == "Correspondance: / Correspondence:").idxmax(), 1]
    applicant_correspondence_language = correspondence_language.split(" / ")[1]
    print("Correspondence Language: " + applicant_correspondence_language)
    return applicant_correspondence_language


def parse_interview_language(item):
    table = item[[0, 1]]
    interview_language = table.loc[(table[0] == "Entrevue / Interview:").idxmax(), 1]
    applicant_interview_language = interview_language.split(" / ")[1]
    print("Interview Language: " + applicant_interview_language)
    return applicant_interview_language


def fill_in_single_line_arguments(item, applicant):
    first_column = item[item.columns[0]].astype(str)

    if first_column.str.contains("Citoyenneté / Citizenship:").any():
        applicant.citizenship = parse_citizenship(item)
    if first_column.str.contains("Droit de priorité / Priority entitlement:").any():
        applicant.priority = parse_priority(item)
    if first_column.str.contains("Préférence aux anciens combattants / Preference to veterans:").any():
        applicant.veteran_preference = parse_is_veteran(item)
    if first_column.str.contains("Première langue officielle / First official language:").any():
        applicant.first_official_language = parse_first_official_language(item)
    if first_column.str.contains("Connaissance pratique / Working ability:").any():
        working_ability = parse_working_ability(item)
        applicant.french_working_ability = parse_french_ability(working_ability)
        applicant.english_working_ability = parse_english_ability(working_ability)
    if first_column.str.contains("Examen écrit / Written exam:").any():
        applicant.written_exam = parse_written_exam_language(item)
    if first_column.str.contains("Correspondance: / Correspondence:").any():
        applicant.correspondence = parse_corresponsence_language(item)
    if first_column.str.contains("Entrevue / Interview:").any():
        applicant.interview = parse_interview_language(item)

    return applicant


def correct_split_item(idx, tables, item):
    if ((idx + 1) != len(tables)) and not str(item.shape) == "(1, 1)":
        item2 = tables[idx + 1]

        if item2.empty:
            return item

        if item2.iloc[0, 0] == "NaN":
            item.iloc[-1, -1] = item.iloc[-1, -1] + item2.iloc[0, 1]

    return item


def find_essential_details(tables):

    applicant = Applicant

    for idx, item in enumerate(tables):

        if item.empty:
            continue
        # tables = merge_questions(tables, item, idx)
        item = correct_split_item(idx, tables, item)
        applicant = fill_in_single_line_arguments(item, applicant)

    applicant.applicant_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(20))


    return applicant


def is_question(item):
    first_column = item[item.columns[0]]

    if first_column.str.contains("Question - Français / French:").any():
        return True
    return False


def merge_questions(df, item, idx):
    if is_question(item):
        for index, item2 in enumerate(df, idx):
            if item2.empty:
                del df[index]
                continue
            first_column = item2[item2.columns[0]]
            if first_column.str.contains("Question - Français / French:").any():
                break
            elif first_column.str.contains("No SRFP / PSRS no:").any():
                break
            else:
                item = pd.concat([item, item2])
                del df[index]

    return df


def clean_and_parse(df, application):
    array = []
    count = 0
    for idx, item in enumerate(df):
        if item.empty:
            del df[idx]
            continue
        else:
            item = item.replace(r'\r', ' ', regex=True)
            item.dropna(axis=1, how='all', inplace=True)
            item.reset_index(drop=True, inplace=True)
            df[idx] = item

            first_column = item[item.columns[0]]
            if first_column.str.contains("Citoyenneté / Citizenship:").any():
                count = count + 1
                array.append(idx)

    print("Applicants: " + str(count))
    for x in range(len(array)):
        if x == (count - 1):
            print("Processing Applicant: " + str(x + 1))
            find_essential_details(df[array[x]:])
        else:
            print("Processing Applicant: " + str(x + 1))
            find_essential_details(df[array[x]:array[x + 1]])

    return application


def parse_application(request):
    if request.pdf.name:
        application = []
        print(request.pdf.name)
        df = tabula.read_pdf("/code/applications/" + request.pdf.name, options, pages="all", multiple_tables="true", lattice="true")
        application = clean_and_parse(df, application)
        return application
    else:
        return {'errors': ErrorMessages.incorrect_pdf_file}