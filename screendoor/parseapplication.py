from .models import Applicant, Position, FormQuestion, Education, Stream, Classification, FormAnswer
from .NLP.helpers.format_text import reprocess_line_breaks, strip_bullet_points
from .NLP.run_NLP_scripts import generate_nlp_extracts
from .models import Applicant, Position, FormQuestion, Education, Stream, Classification, FormAnswer, NlpExtract
import random
import re
import string

import pandas as pd
import tabula
from celery import current_task
from fuzzywuzzy import fuzz
from pandas import options


###################
# Functions to determine what type of information is contained in an item
###################

def is_question(item):
    first_column = item[item.columns[0]]
    return first_column.str.startswith("Question - Français").any()


def is_qualification(item):
    first_column = item[item.columns[0]]
    return first_column.str.contains("Question - Français / French:").any()


def is_stream(item):
    if not str(item.shape) == "(1, 1)":
        for index, row in item.iterrows():
            found_string = item.iloc[index, 1]
            if re.search(r"^Are you applying", found_string, re.IGNORECASE):
                return True

    return False


def is_education(item):
    first_column = item[item.columns[0]]
    return first_column.str.contains("Niveau d'études / Academic Level:").any()


def is_classification(item):
    for index, row in item.iterrows():
        found_string = item.iloc[index, 0]
        ratio = fuzz.partial_ratio("Situation professionnelle", found_string)
        if ratio > 90:
            return True

    return False


###################
# Helper functions that perform minor tasks (formatting/checks)
###################

def is_final_answer(item):
    applicant_answer = get_column_value(
        "Réponse du postulant / Applicant Answer:", item)
    return applicant_answer.lower == "nan"


def check_if_table_valid(table):
    # Checks if the table is a dataframe, not empty, and isn't None.
    return (isinstance(table, pd.DataFrame)) and (not table.empty) and (table is not None)


def clean_data(x):
    x = re.sub(r'\r', '\n', x)
    x = re.sub(r'\n', ' ', x)
    x = re.sub(r'jJio', '\n', x)
    return x.strip()


def text_between(start_string, end_string, text):
    # Effectively returns the string between the first occurrence of start_string and end_string in text
    extracted_text = text.split(start_string, 1)[1].split(end_string, 1)[0]

    return extracted_text


def get_column_value(search_string, item):
    pairings = dict(zip(item[0], item[1]))

    for key in pairings.keys():
        if fuzz.partial_ratio(search_string, key) >= 90:
            return pairings[key]
    return "N/A"


def retrieve_question(table, all_questions):
    question_text = parse_question_text(
        table).replace('\n', " ").replace(" ", "")

    for other_question in all_questions:
        other_question_text = other_question.question_text.replace(
            '\n', " ").replace(" ", "")
        if fuzz.ratio(question_text, other_question_text) > 95:
            return other_question
    # print("NOT A MATCH, THERE WAS AN ERROR IN MATCHING ANSWER")
    return None


def create_short_question_text(long_text):
    if "*Recent" in long_text:
        return long_text.split("*Recent", 1)[0]
    elif "**Significant" in long_text:
        return long_text.split("*Significant", 1)[0]
    elif "*Significant" in long_text:

        return long_text.split("*Significant", 1)[0]
    else:
        return long_text


def find_and_get_req(position, question_text):
    best_req = 0

    for requirement in position.requirement_set.all():
        comparison = fuzz.partial_ratio(requirement.description, question_text)
        if comparison > best_req:
            best_req = comparison
            best_matched_requirement = requirement

    if fuzz.partial_ratio(best_matched_requirement.description, question_text) > 85:
        return best_matched_requirement
    else:
        return None


def does_exist(question, all_questions):
    question_text = question.question_text.replace('\n', " ").replace(" ", "")

    for other_question in all_questions:
        other_question_text = other_question.question_text.replace(
            '\n', " ").replace(" ", "")
        if fuzz.ratio(question_text, other_question_text) > 95:
            return True
    # print("QUESTION DOES NOT EXIST")

    return False


def split_on_slash_take_second(str):
    return str.replace('\n', ' ').split(" / ")[1]


###################
# Functions that deal with one-line values for applicants
###################

def parse_citizenship(item):
    applicant_citizenship = get_column_value(
        "Citoyenneté / Citizenship:", item)
    if "Canadian Citizen" in applicant_citizenship:
        applicant_citizenship = "Canadian Citizen"
    return applicant_citizenship


def parse_working_ability(item):
    working_ability = get_column_value(
        "Connaissance pratique / Working ability:", item)
    return working_ability


def parse_english_ability(working_ability):
    english_working_ability = working_ability.replace('\n', ' ').split(
        "Anglais / English:", 1)[1].split(" / ")[1]

    return english_working_ability


def parse_french_ability(working_ability):
    french_working_ability = split_on_slash_take_second(
        text_between("Français / French :", "Anglais / English:",
                     working_ability))
    return french_working_ability


# Generic function
def parse_single_line_boolean(defining_string, item):
    value = get_column_value(defining_string, item)
    if "No" in value:
        return "False"
    else:
        return "True"


# Generic function
def parse_single_line_value(defining_string, item):
    value = get_column_value(defining_string, item)
    return split_on_slash_take_second(value)


def fill_in_single_line_arguments(item, applicant):
    # Fill in single line entries that require very little processing.
    first_column = item[item.columns[0]].astype(str)
    if first_column.str.startswith("Citoyenneté").any():
        applicant.citizenship = parse_citizenship(item)

    if first_column.str.startswith("Droit de priorité").any():
        applicant.priority = parse_single_line_boolean("Droit de priorité / Priority entitlement:", item)

    if first_column.str.contains("combattants").any():
        applicant.veteran_preference = parse_single_line_boolean("anciens combattants", item)

    if first_column.str.startswith("Première langue officielle").any():
        applicant.first_official_language = parse_single_line_value(
            "Première langue officielle / First official language:", item)

    if first_column.str.startswith("Connaissance pratique").any():
        working_ability = parse_working_ability(item)
        applicant.french_working_ability = parse_french_ability(working_ability)
        applicant.english_working_ability = parse_english_ability(working_ability)

    if first_column.str.contains("Examen écrit / Written exam:").any():
        applicant.written_exam = parse_single_line_value("Examen écrit / Written exam:", item)

    if first_column.str.contains("Correspondance: / Correspondence:").any():
        applicant.correspondence = parse_single_line_value("Correspondance: / Correspondence:", item)

    if first_column.str.contains("Entrevue / Interview:").any():
        applicant.interview = parse_single_line_value("Entrevue / Interview:", item)

    return applicant


###################
# Corrective functions to mend the nuances caused by the limitations of pdf
###################

def correct_split_item(tables):
    # Corrects splits between tables. (Not including splits between questions or educations)
    for index, item in enumerate(tables):

        if check_if_table_valid(item):
            if ((index + 1) != len(tables)) and not str(item.shape) == "(1, 1)":
                item2 = tables[index + 1]

                if item2.empty:
                    if (index + 2) != len(tables):
                        item2 = tables[index + 2]

                if check_if_table_valid(item2):
                    if "nan" == item2.iloc[0, 0].lower():
                        item.iloc[-1, -1] = item.iloc[-1, -1] + \
                                            item2.iloc[0, 1]
                        item2 = item2.iloc[1:, ]
                        item = pd.concat([item, item2], ignore_index=True)
                        tables[index] = item
                        tables[index + 1] = None
                    elif str(item2.shape) == "(1, 1)":
                        if "AUCUNE / NONE" not in item2.iloc[0, 0]:
                            item.iloc[-1, 0] = item.iloc[-1, 0] + \
                                               item2.iloc[0, 0]
                            tables[index] = item
                            tables[index + 1] = None

    return tables


# Generic function
def merge_elements(tables, is_element_type, exclusion_tuple):
    for index, item in enumerate(tables):

        if check_if_table_valid(item) and is_element_type(item):

            if (index + 1) != len(tables):

                for second_index, second_table in enumerate(tables[index + 1:],
                                                            index + 1):

                    if second_table is None or second_table.empty:
                        for idx, table in enumerate(tables[index + 1:],
                                                    second_index):
                            if check_if_table_valid(table):
                                second_table = table
                                break

                    if check_if_table_valid(second_table):
                        second_table_column = second_table[
                            second_table.columns[0]]
                        if second_table_column.str.startswith(exclusion_tuple).any():
                            break
                        else:
                            item = pd.concat(
                                [item, second_table], ignore_index=True)
                            tables[index] = item
                            tables[second_index] = None

    return tables


###################
# Functions that parse data related to applicant questions and answers
###################

def parse_question_text(item):
    question_text = get_column_value("Question - Anglais", item)
    return reprocess_line_breaks(question_text)


def parse_complementary_question_text(item):
    complementary_question_text = get_column_value("Complementary Question", item)
    return reprocess_line_breaks(complementary_question_text)


def parse_applicant_answer(item):
    applicant_answer = get_column_value(
        "Réponse du postulant / Applicant Answer:", item)
    if "No" in applicant_answer:
        applicant_answer = "False"
    else:
        applicant_answer = "True"

    return applicant_answer


def parse_applicant_complementary_response(item):
    first_column = item[item.columns[0]].astype(str)

    if first_column.str.startswith("Réponse Complémentaire").any():
        table = item[[0, 1]]
        applicant_complementary_response = table.loc[
            (table[0].str.startswith("Réponse Complémentaire")).idxmax(), 0]
        applicant_complementary_response = applicant_complementary_response.split("Answer:", 1)[
            1]
        applicant_complementary_response = re.sub(
            r'\\r', '\n', applicant_complementary_response)

        return reprocess_line_breaks(applicant_complementary_response)
    elif is_final_answer(item):
        applicant_answer = get_column_value(
            "Réponse du postulant / Applicant Answer:", item)

        return reprocess_line_breaks(applicant_answer)
    else:
        return None


###################
# Retrieval functions for questions/answers, with specific conditions
###################

def get_question(table, position):
    # Creates a list of questions cross checked for redundancy against previously made questions.
    if is_question(table) and not is_stream(table):
        question_text = parse_question_text(table)
        question = FormQuestion(question_text=question_text,
                                complementary_question_text=parse_complementary_question_text(
                                    table),
                                short_question_text=create_short_question_text(
                                    question_text),
                                parent_requirement=find_and_get_req(
                                    position, question_text)
                                )

        all_questions = position.questions.all()
        if does_exist(question, all_questions):
            return
        else:
            question.parent_position = position
            question.save()
    return


def get_answer(table, answers, position):
    # Creates a list of answers and finds the corresponding question from the questions attached to the position.
    all_questions = position.questions.all()
    if is_question(table) and not is_stream(table):
        linked_question = retrieve_question(table, all_questions)
        comp_response = parse_applicant_complementary_response(table)

        if comp_response is not None:
            comp_response = strip_bullet_points(str.strip(comp_response))

        answer = FormAnswer(applicant_answer=parse_applicant_answer(table),
                            applicant_complementary_response=comp_response,
                            parent_question=linked_question)
        if not (comp_response is None):
            answer.save()
            closing_date = linked_question.parent_position.date_closed
            generate_nlp_extracts(comp_response, linked_question, answer, closing_date)
        answers.append(answer)
    return answers


###################
# Education Parsing
###################

# Given a string that defines a column with certain information, retrieve
# the information if it exists where it should be.
def parse_education_detail(defining_string, item):
    first_column = item[item.columns[0]].astype(str)

    if first_column.str.contains(defining_string).any():
        return get_column_value(defining_string, item)
    else:
        return None


def get_education(item, educations):
    # Makes a list of educations.
    if is_education(item):
        educations.append(
            Education(academic_level=parse_education_detail(
                "Niveau d'études / Academic Level:", item),

                area_of_study=parse_education_detail(
                    "Domaine d'études / Area of Study:", item),

                specialization=parse_education_detail(
                    "Domaine de spécialisation / Specialization:", item),

                program_length=parse_education_detail(
                    "Longueur du programme (Années) / Program Length (Years):", item),

                num_years_completed=parse_education_detail(
                    "Années complétées / Nbr of Years Completed:", item),

                institution=parse_education_detail(
                    "Établissement d'enseignement / Institution:", item),

                graduation_date=parse_education_detail(
                    "Date de graduation / Graduation Date:", item)))
    return educations


###################
# Stream Parsing
###################

def parse_stream(item):
    print(item)
    stream_list = []
    for index, row in item.iterrows():
        key = item.iloc[index, 0]
        value = item.iloc[index, 1]
        if fuzz.partial_ratio("Question - Anglais / English:", key) > 80:
            if re.search("^Are you applying(?!.+and)", value, re.IGNORECASE):
                stream_list = re.findall(r'Stream \d+', value, re.IGNORECASE)
            else:
                return None
        if fuzz.partial_ratio("Réponse du postulant / Applicant Answer:", key) > 80:
            if len(stream_list) == 1 and "Yes" in value:
                return stream_list[0]

    return None


def parse_stream_description(item):
    stream_text = ""
    for index, row in item.iterrows():
        key = item.iloc[index, 0]
        value = item.iloc[index, 1]
        if fuzz.partial_ratio("Question - Anglais / English:", key) > 80:
            stream_text = re.split(r'\d+', value, 1)[1]
        if fuzz.partial_ratio("Réponse du postulant / Applicant Answer:", key) > 80:
            if "Yes" in value:
                stream_text = stream_text.replace(",", "")
                stream_text = stream_text.replace("?", "")

                return stream_text
    return None


def parse_stream_response(item):
    for index, row in item.iterrows():
        key = item.iloc[index, 0]
        value = item.iloc[index, 1]
        if fuzz.partial_ratio("Réponse du postulant / Applicant Answer:", key) > 80:
            if "Yes" in value:
                return True
            elif "No" in value:
                return False

    return None


def get_streams(item, streams):
    # Makes a list of streams.
    if is_stream(item):
        if parse_stream(item) is None:
            return streams
        else:
            streams.append(Stream(stream_name=parse_stream(item),
                                  stream_response=parse_stream_response(item),
                                  stream_description=parse_stream_description(item)))
    return streams


###################
# Classification Parsing
###################

def parse_classification_value(defining_string, item):
    for index, row in item.iterrows():
        found_string = item.iloc[index, 0]
        if fuzz.partial_ratio(defining_string, found_string) > 90:
            classification = item.iloc[index, 1]
            return classification

    return None


def get_classifications(item, classifications):
    # Makes a list of classifications.
    if is_classification(item):
        classifications.append(
            Classification(classification_substantive=parse_classification_value("Substantive group and level", item),
                           classification_current=parse_classification_value("Current group and level", item)))
    return classifications


###################
# High level controller functions
###################

def find_essential_details(tables, position):
    # Fills out an applicant details based on the list of tables provided.
    applicant = Applicant()
    applicant.save()
    position.save()
    streams = []
    answers = []
    classifications = []
    educations = []

    tables = correct_split_item(tables)
    tables = merge_elements(tables, is_question, (
        ("Question - Français / French:", "No SRFP / PSRS no:", "Poste disponible / Job Opportunity:")))
    tables = merge_elements(tables, is_education, ("Niveau d'études", "Province", "Type d'emploi"))

    for table_counter, item in enumerate(tables):
        if check_if_table_valid(item):
            get_question(item, position)
            answers = get_answer(item, answers, position)
            educations = get_education(item, educations)
            streams = get_streams(item, streams)
            classifications = get_classifications(item, classifications)
            applicant = fill_in_single_line_arguments(item, applicant)

    applicant.applicant_id = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(20))

    # save each item to the applicant
    for item in (answers + educations + streams + classifications):
        item.parent_applicant = applicant
        item.save()

    return applicant


def clean_and_parse(data_frames, position, task_id, total_applicants, applicant_counter):
    # Pre-processing of the tables to insure for easy processing and string matching.
    applications = []
    applicant_page_numbers = []
    applicant_count = 0

    for index, data_frame in enumerate(data_frames):
        if not data_frame.empty:
            data_frame = data_frame.astype(str)
            data_frame = data_frame.applymap(clean_data)
            data_frame.dropna(axis=1, how='all', inplace=True)
            data_frame.reset_index(drop=True, inplace=True)
            data_frames[index] = data_frame
            table_column_1 = data_frame[data_frame.columns[0]]
            if table_column_1.str.contains("Citoyenneté / Citizenship:").any():
                applicant_count += 1
                applicant_page_numbers.append(index)

    for current_applicant in range(len(applicant_page_numbers)):
        current_task.update_state(task_id=task_id, state='PROGRESS', meta={
            'current': applicant_counter + current_applicant + 1, 'total': total_applicants})
        if current_applicant == (applicant_count - 1):
            print("Processing Applicant: " + str(current_applicant + 1))
            applications.append(find_essential_details(
                data_frames[applicant_page_numbers[current_applicant]:], position))
        else:
            print("Processing Applicant: " + str(current_applicant + 1))
            applications.append(find_essential_details(
                data_frames[applicant_page_numbers[current_applicant]:applicant_page_numbers[current_applicant + 1]],
                position))

    return applications


def get_total_applicants(filepaths, task_id):
    count = 0
    for filepath in filepaths:
        df = tabula_read_pdf(filepath)
        for idx, item in enumerate(df):
            if not item.empty:
                first_column = item[item.columns[0]]
                if first_column.str.contains("Citoyenneté / Citizenship:").any():
                    count += 1
                    current_task.update_state(task_id=task_id, state='PENDING', meta={
                        'total': count})
    return count


def tabula_read_pdf(file_path):
    return tabula.read_pdf(file_path, options, pages="all",
                           multiple_tables="true",
                           lattice="true")
