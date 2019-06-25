import random
import random
import string

import pandas as pd
import tabula
from fuzzywuzzy import fuzz
from pandas import options

from screendoor.NLP.howextraction import extract_how
from screendoor.NLP.whenextraction import extract_dates
from screendoor.models import Applicant, FormQuestion, Education, Stream, Classification, FormAnswer


def is_question(item):
    first_column = item[item.columns[0]]

    if first_column.str.startswith("Question - Français").any():
        return True
    return False


def is_in_questions(table, question_list):
    if is_question(table):
        for item in question_list:
            if fuzz.ratio(item.question_text, parse_question_text(table)) > 80:
                return True

    return False


def is_qualification(item):
    first_column = item[item.columns[0]]

    if first_column.str.contains("Question - Français / French:").any():
        return True
    return False


def is_stream(item):
    if not str(item.shape) == "(1, 1)":
        value_column = item[item.columns[1]]

        if value_column.str.startswith("Are you applying for Stream").any():
            return True
        elif value_column.str.startswith("Are you applying to Stream").any():
            return True

    return False


def is_education(item):
    first_column = item[item.columns[0]]

    if first_column.str.contains("Niveau d'études / Academic Level:").any():
        return True
    return False


def is_classification(item):
    for index, row in item.iterrows():
        found_string = item.iloc[index, 0]
        ratio = fuzz.partial_ratio("Situation professionnelle", found_string)
        if ratio > 90:
            return True

    return False


def is_final_answer(item):
    table = item[[0, 1]]
    applicant_answer = table.loc[(table[0] == "Réponse du postulant / Applicant Answer:").idxmax(), 1]

    if applicant_answer == "NaN":
        return True
    else:
        return False


def check_if_table_valid(table):
    # Checks if the table is a dataframe, not empty, and isn't None.
    return (isinstance(table, pd.DataFrame)) and (not table.empty) and (table is not None)


def clean_data(x):
    if "Réponse Complémentaire: / Complementary Answer:" not in x:
        x = x.replace(r'\r', ' ', regex=True)
    return x


def text_between(start_string, end_string, text):
    # Effectively returns the string between the first occurrence of start_string and end_string in text
    extracted_text = text.split(start_string, 1)[1].split(end_string, 1)[0]

    return extracted_text


def get_column_value(search_string, table):
    for row_num, (key, val) in enumerate(table.iteritems()):
        if fuzz.partial_ratio(search_string, key) >= 80:
            return val


def retrieve_question(table, question_list):
    if is_question(table):
        for item in question_list:
            if fuzz.ratio(item.question_text, parse_question_text(table)) > 80:
                return item

    return None


def parse_citizenship(item):
    table = item[[0, 1]]
    applicant_citizenship = table.loc[(table[0] == "Citoyenneté / Citizenship:").idxmax(), 1]
    if "Canadian Citizen" in applicant_citizenship:
        applicant_citizenship = "Canadian Citizen"
    return applicant_citizenship


def parse_priority(item):
    table = item[[0, 1]]
    applicant_has_priority = \
        table.loc[(table[0] == "Droit de priorité / Priority entitlement:").idxmax(), 1]
    if "No" in applicant_has_priority:
        applicant_has_priority = "False"
    else:
        applicant_has_priority = "True"
    return applicant_has_priority


def parse_is_veteran(item):
    table = item[[0, 1]]
    applicant_is_veteran = table.loc[
        (table[0] == "Préférence aux anciens combattants / Preference to veterans:").idxmax(), 1]
    if "No" in applicant_is_veteran:
        applicant_is_veteran = "False"
    else:
        applicant_is_veteran = "True"
    return applicant_is_veteran


def parse_first_official_language(item):
    table = item[[0, 1]]
    first_official_language = \
        table.loc[(table[0] == "Première langue officielle / First official language:").idxmax(), 1]
    applicant_first_official_language = first_official_language.split(" / ")[1]
    return applicant_first_official_language


def parse_working_ability(item):
    table = item[[0, 1]]
    working_ability = table.loc[(table[0] == "Connaissance pratique / Working ability:").idxmax(), 1]
    return working_ability


def parse_english_ability(working_ability):
    english_working_ability = working_ability.split("Anglais / English:", 1)[1].split(" / ")[1]

    return english_working_ability


def parse_french_ability(working_ability):
    french_working_ability = \
        text_between("Français / French :", "Anglais / English:", working_ability).split(" / ")[1]
    return french_working_ability


def parse_written_exam_language(item):
    table = item[[0, 1]]
    written_exam_language = table.loc[(table[0] == "Examen écrit / Written exam:").idxmax(), 1]
    applicant_written_exam_language = written_exam_language.split(" / ")[1]
    return applicant_written_exam_language


def parse_corresponsence_language(item):
    table = item[[0, 1]]
    correspondence_language = table.loc[(table[0] == "Correspondance: / Correspondence:").idxmax(), 1]
    applicant_correspondence_language = correspondence_language.split(" / ")[1]
    return applicant_correspondence_language


def parse_interview_language(item):
    table = item[[0, 1]]
    interview_language = table.loc[(table[0] == "Entrevue / Interview:").idxmax(), 1]
    applicant_interview_language = interview_language.split(" / ")[1]
    return applicant_interview_language


def parse_question_text(item):
    table = item[[0, 1]]

    question_text = table.loc[(table[0].str.startswith("Question - Anglais")).idxmax(), 1]
    return question_text


def parse_complementary_question_text(item):
    table = item[[0, 1]]
    complementary_question_text = table.loc[(table[0].str.startswith("Complementary Question")).idxmax(), 1]
    return complementary_question_text


def parse_applicant_answer(item):
    table = item[[0, 1]]
    applicant_answer = table.loc[(table[0] == "Réponse du postulant / Applicant Answer:").idxmax(), 1]

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
        applicant_complementary_response = applicant_complementary_response.split("Complementary Answer:")[1]
        return applicant_complementary_response
    elif is_final_answer(item):
        table = item[[0, 1]]
        applicant_answer = table.loc[(table[0] == "Réponse du postulant / Applicant Answer:").idxmax(), 0].split(
            "Réponse du postulant / Applicant Answer:", 1)[1]
        return applicant_answer
    else:
        return None


def parse_academic_level(item):
    first_column = item[item.columns[0]].astype(str)

    if first_column.str.contains("Niveau d'études / Academic Level:").any():
        table = item[[0, 1]]
        academic_level = table.loc[(table[0] == "Niveau d'études / Academic Level:").idxmax(), 1]
        return academic_level
    else:
        return None


def parse_area_of_study(item):
    first_column = item[item.columns[0]].astype(str)

    if first_column.str.contains("Domaine d'études / Area of Study:").any():
        table = item[[0, 1]]
        area_of_study = table.loc[(table[0] == "Domaine d'études / Area of Study:").idxmax(), 1]
        return area_of_study
    else:
        return None


def parse_specialization(item):
    first_column = item[item.columns[0]].astype(str)

    if first_column.str.contains("Domaine de spécialisation / Specialization:").any():
        table = item[[0, 1]]
        specialization = table.loc[(table[0] == "Domaine de spécialisation / Specialization:").idxmax(), 1]

        return specialization
    else:
        return None


def parse_program_length(item):
    first_column = item[item.columns[0]].astype(str)

    if first_column.str.contains("Longueur du programme").any():
        table = item[[0, 1]]
        program_length = table.loc[(table[0] == "Longueur du programme (Années) / Program Length (Years):").idxmax(), 1]

        return program_length
    else:
        return None


def parse_num_years_completed(item):
    first_column = item[item.columns[0]].astype(str)

    if first_column.str.contains("Années complétées / Nbr of Years Completed:").any():
        table = item[[0, 1]]
        num_years_completed = table.loc[(table[0] == "Années complétées / Nbr of Years Completed:").idxmax(), 1]

        return num_years_completed
    else:
        return None


def parse_institution(item):
    first_column = item[item.columns[0]].astype(str)

    if first_column.str.contains("Établissement d'enseignement / Institution:").any():
        table = item[[0, 1]]
        institution = table.loc[(table[0] == "Établissement d'enseignement / Institution:").idxmax(), 1]

        return institution
    else:
        return None


def parse_graduation_date(item):
    first_column = item[item.columns[0]].astype(str)

    if first_column.str.contains("Date de graduation / Graduation Date:").any():
        table = item[[0, 1]]
        graduation_date = table.loc[(table[0] == "Date de graduation / Graduation Date:").idxmax(), 1]

        return graduation_date
    else:
        return None


def parse_current(item):
    for index, row in item.iterrows():
        found_string = item.iloc[index, 0]
        if fuzz.partial_ratio("Current group and level", found_string) > 90:
            current_classification = item.iloc[index, 1]
            return current_classification

    return None


def parse_substantive(item):
    for index, row in item.iterrows():
        found_string = item.iloc[index, 0]
        if fuzz.partial_ratio("Substantive group and level", found_string) > 90:
            substantive_classification = item.iloc[index, 1]
            return substantive_classification

    return None


def parse_stream(item):
    first_column = item[item.columns[0]].astype(str)
    value_column = item[item.columns[1]].astype(str)
    if value_column.str.contains(r"^Are you applying for Stream \d", regex=True).any():
        table = item[[0, 1]]

        stream_text = table.loc[(table[0] == "Question - Anglais / English:").idxmax(), 1]
        stream_text = stream_text.split("Are you applying for")[1].split(",")[0]

        if first_column.str.contains("Réponse du postulant / Applicant Answer:").any():
            table = item[[0, 1]]
            response = table.loc[(table[0] == "Réponse du postulant / Applicant Answer:").idxmax(), 1]

            if "Yes" in response:
                return stream_text
    elif value_column.str.contains(r"^Are you applying to Stream \d", regex=True).any():
        table = item[[0, 1]]
        stream_text = table.loc[(table[0] == "Question - Anglais / English:").idxmax(), 1]
        stream_text = stream_text.split("Are you applying to")[1].split("?")[0]

        if first_column.str.contains("Réponse du postulant / Applicant Answer:").any():
            table = item[[0, 1]]
            response = table.loc[(table[0] == "Réponse du postulant / Applicant Answer:").idxmax(), 1]

            if "Yes" in response:
                return stream_text
    else:
        return None


def fill_in_single_line_arguments(item, applicant):
    # Fill in single line entries that require very little processing.
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
                    if "NaN" in item2.ix[0, 0]:
                        item.iloc[-1, -1] = item.iloc[-1, -1] + item2.iloc[0, 1]
                        item2 = item2.iloc[1:, ]
                        item = pd.concat([item, item2], ignore_index=True)
                        tables[index] = item
                        tables[index + 1] = None
                    elif str(item2.shape) == "(1, 1)":
                        if "AUCUNE / NONE" not in item2.iloc[0, 0]:
                            item.iloc[-1, 0] = item.iloc[-1, 0] + item2.iloc[0, 0]
                            tables[index] = item
                            tables[index + 1] = None

    return tables


def merge_questions(tables):
    # Merges questions.
    for index, item in enumerate(tables):

        if check_if_table_valid(item) and is_question(item):

            if (index + 1) != len(tables):

                for second_index, second_table in enumerate(tables[index + 1:], index + 1):

                    if second_table is None or second_table.empty:
                        for idx, table in enumerate(tables[index + 1:], second_index):
                            if check_if_table_valid(table):
                                second_table = table
                                break

                    if check_if_table_valid(second_table):
                        second_table_column = second_table[second_table.columns[0]]
                        if second_table_column.str.startswith("Question - Français / French:").any():
                            break
                        elif second_table_column.str.startswith("No SRFP / PSRS no:").any():
                            break
                        elif second_table_column.str.startswith("Poste disponible / Job Opportunity:").any():
                            break
                        else:
                            item = pd.concat([item, second_table], ignore_index=True)
                            tables[index] = item
                            tables[second_index] = None

    return tables


def merge_educations(tables):
    # Merges Educations.

    for index, item in enumerate(tables):

        if check_if_table_valid(item) and is_education(item):

            if (index + 1) != len(tables):

                for second_index, second_table in enumerate(tables[index + 1:], index + 1):
                    if second_table is None or second_table.empty:
                        for idx, table in enumerate(tables[index + 1:], second_index):
                            if check_if_table_valid(table):
                                second_table = table
                                break
                    if check_if_table_valid(second_table):
                        second_table_column = second_table[second_table.columns[0]]
                        if second_table_column.str.startswith("Niveau d'études").any():
                            break
                        elif second_table_column.str.startswith("Province").any():
                            break
                        elif second_table_column.str.startswith("Type d'emploi").any():
                            break
                        else:
                            item = pd.concat([item, second_table], ignore_index=True)
                            tables[index] = item
                            tables[second_index] = None

    return tables


def create_short_question_text(long_text):
    if "*Recent" in long_text:
        return long_text.split("*Recent", 1)[0]
    elif "**Significant" in long_text:
        return long_text.split("*Significant", 1)[0]
    elif "*Significant" in long_text:

        return long_text.split("*Significant", 1)[0]
    else:
        return long_text


def get_question(table, questions, position):
    # Creates a list of questions cross checked for redundancy against previously made questions.
    if is_question(table) and not is_stream(table):

        question = FormQuestion(question_text=parse_question_text(table),
                                complementary_question_text=parse_complementary_question_text(table),
                                short_question_text=create_short_question_text(parse_question_text(table))
                                )

        all_questions = position.questions.all()
        for item in all_questions:
            if item.question_text.replace(" ", "") == question.question_text.replace(" ", ""):
                return questions

        question.parent_position = position
        question.save()
        questions.append(question)

    return questions


def get_answer(table, answers, position):
    # Creates a list of answers and finds the corresponding question from the questions attached to the position.
    all_questions = position.questions.all()

    if is_in_questions(table, all_questions) and not is_stream(table):
        analysis = None
        comp_response = parse_applicant_complementary_response(table)
        if not (comp_response is None):
            # Extract dates, and convert the returned dict to a flat list
            dates = [': '.join((k, v)) for k, v in
                     extract_dates(comp_response).items()]
            # Extract actions
            experiences = extract_how(comp_response)
            # Combine the two lists, and make them a newline delimited str.
            if dates == [] and experiences == []:
                analysis = "No Analysis"
            else:
                analysis = '\n'.join(list(dates + experiences))
        answers.append(FormAnswer(applicant_answer=parse_applicant_answer(table),
                                  applicant_complementary_response=comp_response,
                                  parent_question=retrieve_question(table, all_questions),
                                  analysis=analysis))

    return answers


def get_education(item, educations):
    # Makes a list of educations.
    if is_education(item):
        educations.append(Education(academic_level=parse_academic_level(item),
                                    area_of_study=parse_area_of_study(item),
                                    specialization=parse_specialization(item),
                                    program_length=parse_program_length(item),
                                    num_years_completed=parse_num_years_completed(item),
                                    institution=parse_institution(item),
                                    graduation_date=parse_graduation_date(item)))
    return educations


def get_streams(item, streams):
    # Makes a list of streams.
    if is_stream(item):
        streams.append(Stream(stream_name=parse_stream(item)))
    return streams


def get_classifications(item, classifications):
    # Makes a list of classifications.
    if is_classification(item):
        classifications.append(Classification(classification_substantive=parse_substantive(item),
                                              classification_current=parse_current(item)))
    return classifications


def find_essential_details(tables, position):
    # Fills out an applicant details based on the list of tables provided.
    applicant = Applicant()
    applicant.save()
    position.save()
    questions = []
    streams = []
    answers = []
    classifications = []
    educations = []

    tables = correct_split_item(tables)
    tables = merge_questions(tables)
    tables = merge_educations(tables)

    for table_counter, item in enumerate(tables):
        if check_if_table_valid(item):
            questions = get_question(item, questions, position)
            answers = get_answer(item, answers, position)
            educations = get_education(item, educations)
            streams = get_streams(item, streams)
            classifications = get_classifications(item, classifications)
            applicant = fill_in_single_line_arguments(item, applicant)

    applicant.applicant_id = ''.join(
        random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(20))

    for item in answers:
        item.parent_applicant = applicant
        item.save()
    for item in educations:
        item.parent_applicant = applicant
        item.save()
    for item in streams:
        item.parent_applicant = applicant
        item.save()
    for item in classifications:
        item.parent_applicant = applicant
        item.save()

    return applicant


def clean_and_parse(df, application, position, applicant_counter):
    # Pre-processing of the tables to insure for easy processing and string matching.
    array = []
    count = 0

    for idx, item in enumerate(df):
        if item.empty:
            continue
        else:
            item = item.astype(str)
            item = item.apply(clean_data)
            item.dropna(axis=1, how='all', inplace=True)
            item.reset_index(drop=True, inplace=True)
            df[idx] = item

            first_column = item[item.columns[0]]
            if first_column.str.contains("Citoyenneté / Citizenship:").any():
                count = count + 1
                array.append(idx)

    for x in range(len(array)):
        if x == (count - 1):
            print("Processing Applicant: " + str(x + 1 + applicant_counter))
            application.append(find_essential_details(df[array[x]:], position))
        else:
            print("Processing Applicant: " + str(x + 1 + applicant_counter))
            application.append(find_essential_details(df[array[x]:array[x + 1]], position))

    return application


def parse_application(request, position, new_pdf_name, applicant_counter, batch_counter):
    # Parse an application batch.
    if request.pdf.name:
        application = []
        print("BATCH " + str(batch_counter) + ": READING TABLES")

        df = tabula.read_pdf("/code/screendoor/applications/" + new_pdf_name, options, pages="all",
                             multiple_tables="true",
                             lattice="true")

        print("BATCH " + str(batch_counter) + ": TABLES SUCCESSFULLY READ")

        application = clean_and_parse(df, application, position, applicant_counter)
        for item in application:
            item.parent_position = position
            item.save()
        return len(application)
