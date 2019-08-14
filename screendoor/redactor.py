import os
import random
import re
import string

import numpy as np
import pandas as pd
import tabula

from fuzzywuzzy import fuzz
from pandas import options
from tika import parser
from weasyprint import HTML, CSS

forbidden = ["Nom de famille / Last Name:", "Prénom / First Name:", "Initiales / Initials:", "No SRFP / PSRS no:",
             "Organisation du poste d'attache / Substantive organization:",
             "Organisation actuelle / Current organization:",
             "Lieu de travail actuel / Current work location:",
             "Lieu de travail du poste d'attache / Substantive work location:",
             "Code d'identification de dossier personnel (CIDP) / Personal Record Identifier (PRI):",
             "Courriel / E-mail:", "Adresse / Address:", "Autre courriel / Alternate E-mail:",
             "Télécopieur / Facsimile:", "Numéro ATS / TTY Number:", "Téléphone / Telephone:",
             "Autre Téléphone / Alternate Telephone:"]


def to_html_pretty(df, title='REDACTED DATA'):
    ht = ''
    if title != '':
        ht += '<h2> %s </h2>\n' % title
    ht += df.to_html(classes='wide', escape=False, index=False, header=False)

    return HTML_TEMPLATE1 + ht + HTML_TEMPLATE2


HTML_TEMPLATE1 = '''
<html>
<head>
<style>
  h2 {
    text-align: center;
    font-family: Helvetica, Arial, sans-serif;
  }
  table { 
    table-layout: auto;
  }
  table, th, td {
    border: 1px solid black;
    border-collapse: collapse;
  }
  th, td {
    padding: 5px;
    text-align: center;
    font-family: Helvetica, Arial, sans-serif;
  }
  table tbody tr:hover {
    background-color: #dddddd;
  }
  .wide {
    width: 90%; 
  }
</style>
</head>
<body>
'''

HTML_TEMPLATE2 = '''
</body>
</html>
'''


def check_if_table_valid(table):
    # Checks if the table is a dataframe, not empty, and isn't None.
    return (isinstance(table, pd.DataFrame)) and (not table.empty) and (table is not None)


def is_valid_cell(string):
    return (string is not None) and (string != "")


def is_question(item):
    first_column = item[item.columns[0]]

    if first_column.str.startswith("Question - Français").any():
        return True
    return False


def clean_question_data(x, spacing_array):
    if is_valid_cell(x):
        x = re.sub(r"\r", "\n", x)
        for item in spacing_array:
            text = item[0]
            line_break_list = item[1]
            if fuzz.partial_ratio(text, x) > 80:
                for linebreak_index in reversed(line_break_list):
                    x = x[:linebreak_index] + '\n' + x[linebreak_index:]
                break
    return x


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
                            item = pd.concat(
                                [item, second_table], ignore_index=True)
                            tables[index] = item
                            tables[second_index] = None

    return tables


def handle_new_lines(tables, spacing_array):
    for index, table in enumerate(tables):
        if table is not None and isinstance(table, pd.DataFrame):

            if is_question(table):
                for idx, row in table.iterrows():
                    cell_1 = table.iloc[idx, 0]
                    for item in spacing_array:
                        text = item
                        if fuzz.ratio(cell_1, text) > 90:
                            table.iloc[idx, 0] = text

            table = table.replace("\r", "\n", regex=True)
            table = table.replace("\\t", " ", regex=True)
            table = table.replace("\n", "jJio", regex=True)
            tables[index] = table

    return tables


def is_stream(item):
    if not str(item.shape) == "(1, 1)":
        value_column = item[item.columns[1]]

        if value_column.str.startswith("Are you applying for Stream").any():
            return True
        elif value_column.str.startswith("Are you applying to Stream").any():
            return True

    return False


def correct_split_item(tables):
    # Corrects splits between tables. (Not including splits between questions or educations)
    for index, item in enumerate(tables):

        if check_if_table_valid(item):
            if ((index + 1) != len(tables)) and not str(item.shape) == "(1, 1)":
                item2 = tables[index + 1]

                if item2 is None or item2.empty:
                    if (index + 2) != len(tables):
                        item2 = tables[index + 2]

                if check_if_table_valid(item2):
                    if "nan" == item2.iloc[0, 0].lower():
                        item.iloc[-1, -1] = item.iloc[-1, -1] + " " + item2.iloc[0, 1]
                        item2 = item2.iloc[1:, ]
                        item = pd.concat([item, item2], ignore_index=True)
                        tables[index] = item
                        tables[index + 1] = None
                    elif str(item2.shape) == "(1, 1)":
                        if "AUCUNE / NONE" not in item2.iloc[0, 0] and not is_stream(item):
                            item.iloc[-1, 0] = item.iloc[-1, 0] + " " + item2.iloc[0, 0]
                            tables[index] = item
                            tables[index + 1] = None

    return tables


def find__previous_legitimate_table(tables, index):
    for idx, table in enumerate(reversed(tables[0:index - 1])):
        if check_if_table_valid(table):
            found_table = table
            break

    return found_table


def remove_all_spacing(text):
    text = text.replace("\n", "")
    text = text.replace("\t", "")
    text = re.sub(r'jJio', "", text)
    text = text.replace(" ", "")
    return text


def remove_tables(tables, resume_string):
    delete = False

    for index, item in enumerate(tables):
        if item is not None and str(item.shape) == "(1, 1)":
            print("STRING TO MATCH: " + remove_all_spacing(resume_string))
            cell_contents = str(item.iloc[0, 0].replace("\r", "\n"))
            print(remove_all_spacing(cell_contents))
            if remove_all_spacing(cell_contents).startswith(remove_all_spacing(resume_string)):
                return tables[:index]

    return tables


def redact_fields(list_of_data_frames):
    for idx, item in enumerate(list_of_data_frames):
        if item is not None and isinstance(item, pd.DataFrame):
            for field in forbidden:
                for index, row in item.iterrows():
                    found_string = item.iloc[index, 0]
                    ratio = fuzz.ratio(field, found_string)
                    if ratio > 70:
                        item.iloc[index, 1] = "REDACTED"

            list_of_data_frames[idx] = item
    return list_of_data_frames


def find_essential_details(list_of_data_frames, spacing_array, resume_string):
    list_of_data_frames = remove_tables(list_of_data_frames, resume_string)
    list_of_data_frames = correct_split_item(list_of_data_frames)
    list_of_data_frames = merge_questions(list_of_data_frames)
    list_of_data_frames = handle_new_lines(list_of_data_frames, spacing_array)
    list_of_data_frames = redact_fields(list_of_data_frames)

    documents = []
    ignore = False

    for idx, item in enumerate(list_of_data_frames):
        if item is None or not isinstance(item, pd.DataFrame):
            continue

        if str(item.shape) == "(1, 1)" and ((idx - 1) >= 0) and is_stream(list_of_data_frames[idx - 1]):
            ignore = True

        if item is not None:
            if item[0].str.contains("Poste disponible / Job Opportunity:").any():
                ignore = False

            if not ignore:
                html = item.to_html(index=False, header=False)
                documents.append(
                    HTML(string=html).render(
                        stylesheets=[
                            CSS(
                                string='table, th, td {border: 1px solid black; border-collapse: collapse; font-size: 7px; vertical-align: middle;}')]))

    pages = []

    for document in documents:
        for page in document.pages:
            pages.append(page)

    return pages


def get_resume_starter_string(text):
    resume_text = text.split("Curriculum vitae / Résumé")[1]
    resume_text = resume_text.replace("\n", "")
    resume_text = re.sub(r'jJio', "", resume_text)
    resume_text = resume_text.strip()
    resume_text = " ".join(resume_text.split(" ", 2)[:2])
    resume_text = resume_text.replace(" ", "")
    print("RESUME TEXT:" + resume_text)

    return resume_text


def get_properly_spaced_text_array(text):
    # Page numbers cleaned out
    text = re.sub(r"\s+Page: [0-9]+ / [0-9]+\s+", "\n", text)
    text = re.sub(r"\s+Qualifications essentielles / Essential Qualifications\s+", "\n", text)
    text = re.sub(r"\s+Qualifications constituant un atout / Asset Qualifications\s+", "\n", text)
    text = re.sub(r"\n\n+", "\n\n", text)

    answer_text_array = []
    while "Complementary Answer:" in text:
        answer_text = "Réponse Complémentaire: / Complementary Answer:\n" + \
                      text.split("Complementary Answer:", 1)[1].split("Question - Français", 1)[0]
        answer_text_array.append(answer_text)
        text = text.replace("Complementary Answer:", "", 1)

    return answer_text_array


def get_tika_text(pdf_file_path):
    fileData = parser.from_file(pdf_file_path)
    text = fileData['content']
    return text


def split_tika_text(tika_text):
    applicant_text_list = []
    if "Liste des postulants / Applicant List" in tika_text:
        applicant_list = \
            tika_text.split("Liste des postulants / Applicant List", 1)[1].split("Information sur le poste", 1)[0]
    else:
        return [tika_text]
    applicant_list = re.findall(r"^\d+\..+", applicant_list, re.MULTILINE)
    for idx, item in enumerate(applicant_list):
        applicant_list[idx] = item.strip("\n")
        applicant_list[idx] = item.strip()
    applicant_list = list(dict.fromkeys(applicant_list))

    main_text = applicant_list[0] + tika_text.split(applicant_list[0], 2)[2]
    for index, applicant_text in enumerate(applicant_list):
        if index == (len(applicant_list) - 1) and applicant_list[index] != "":
            temp_text = main_text.split(applicant_list[index], 1)[1].strip()
            applicant_text_list.append(temp_text)
        elif applicant_list[index] != "":
            temp_text = main_text.split(applicant_list[index], 1)[1]
            temp_text = temp_text.split(applicant_list[index + 1], 1)[0]
            applicant_text_list.append(temp_text)

    return applicant_text_list


def get_first_page(item):
    html = item.to_html(index=False, header=False)
    document = HTML(string=html).render(stylesheets=[CSS(
        string='table, th, td {border: 1px solid black; border-collapse: collapse; font-size: 7px; vertical-align: middle;}')])
    return document


def clean_and_redact(data_frames, pdf_file_path, save_file_path):
    # Pre-processing of the tables to insure for easy processing and string matching.
    applicant_page_numbers = []
    applicant_count = 0
    for index, data_frame in enumerate(data_frames):
        if not data_frame.empty:
            data_frame = data_frame.astype(str)
            data_frame.dropna(axis=1, how='all', inplace=True)
            data_frame.reset_index(drop=True, inplace=True)
            data_frames[index] = data_frame
            table_column_1 = data_frame[data_frame.columns[0]]
            if table_column_1.str.contains("Poste disponible").any():
                applicant_count += 1
                applicant_page_numbers.append(index)

    pages = []

    tika_text = get_tika_text(pdf_file_path)
    applicant_text_array = split_tika_text(tika_text)
    for current_applicant in range(len(applicant_page_numbers)):

        if current_applicant == (applicant_count - 1):
            print("Processing Applicant: " + str(current_applicant + 1))
            text = applicant_text_array[current_applicant]
            spacing_array = get_properly_spaced_text_array(text)
            resume_strings = get_resume_starter_string(text)

            pages += find_essential_details(
                data_frames[applicant_page_numbers[current_applicant]:], spacing_array, resume_strings)
        else:
            print("Processing Applicant: " + str(current_applicant + 1))
            text = applicant_text_array[current_applicant]
            spacing_array = get_properly_spaced_text_array(text)
            resume_strings = get_resume_starter_string(text)

            pages += find_essential_details(
                data_frames[applicant_page_numbers[current_applicant]:applicant_page_numbers[current_applicant + 1]],
                spacing_array, resume_strings)
    document = get_first_page(data_frames[0])
    document.copy(pages).write_pdf(save_file_path)
    pass


def redact_applications():
    pd.set_option('display.max_colwidth', -1)
    count = 0
    if not os.path.isdir("redacted"):
        print("Creating folder redacted...")
        os.mkdir("redacted")

    directory = "sensitive"
    print(os.listdir(directory))
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".pdf"):
                pdf_file_path = os.path.join(root, file)
                print(pdf_file_path)
                df = tabula.read_pdf(pdf_file_path, options, pages="all", multiple_tables="true", guess=False,
                                     lattice="true")
                save_folder_directory = "redacted" + pdf_file_path.strip(directory).strip(file)
                print(save_folder_directory)
                if not os.path.isdir(save_folder_directory):
                    os.mkdir(save_folder_directory)
                new_file_name = ''.join(
                    random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(20))
                save_file_path = "redacted" + pdf_file_path.strip(directory).replace(file, new_file_name + ".pdf")
                print(save_file_path)
                clean_and_redact(df, pdf_file_path, save_file_path)

                continue
            else:
                continue

    return count
