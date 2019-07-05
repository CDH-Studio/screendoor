import os
import re
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
             "Télécopieur / Facsimile:", "Téléphone / Telephone:", "Autre Téléphone / Alternate Telephone:"]


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


def split_complementary_answer(tables):
    return tables


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


def handle_new_lines(table, spacing_array):
    table = table.replace("\r", "\n", regex=True)

    if is_question(table):
        for index, row in table.iterrows():
            cell_1 = table.iloc[index, 0]
            cell_2 = table.iloc[index, 1]
            for item in spacing_array:
                text = item
                if fuzz.ratio(cell_1, text) > 90:
                    table.iloc[index, 0] = text
                if fuzz.ratio(cell_2, text) > 90:
                    table.iloc[index, 1] = text
    table = table.replace("\n", "jJio", regex=True)
    return table


def is_stream(item):
    if not str(item.shape) == "(1, 1)":
        value_column = item[item.columns[1]]

        if value_column.str.startswith("Are you applying for Stream").any():
            return True
        elif value_column.str.startswith("Are you applying to Stream").any():
            return True

    return False


def find_essential_details(list_of_data_frames, spacing_array):
    list_of_data_frames = split_complementary_answer(list_of_data_frames)
    for idx, item in enumerate(list_of_data_frames):
        if item is None or item[0].dtype == np.float64 or item[0].dtype == np.int64:
            continue
        else:
            item = handle_new_lines(item, spacing_array)
            for field in forbidden:
                for index, row in item.iterrows():
                    found_string = item.iloc[index, 0]
                    ratio = fuzz.ratio(field, found_string)
                    if ratio > 70:
                        item.iloc[index, 1] = "REDACTED"

            list_of_data_frames[idx] = item

    documents = []
    ignore = False

    for idx, item in enumerate(list_of_data_frames):
        if item is None or item[0].dtype == np.float64 or item[0].dtype == np.int64:
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
    resume_text = text.split("Curriculum vitae / Résumé\n")[1]
    resume_text = resume_text.replace("\n", "")
    resume_text = resume_text.replace("\n", "")
    resume_text = re.sub(r'jJio', "", resume_text)
    resume_text = resume_text.strip()
    resume_text = " ".join(resume_text.split(" ", 2)[:2])
    resume_text = resume_text.replace(" ", "")

    return resume_text


def get_spacing_array_of_tuples(text):
    # Page numbers cleaned out
    text = re.sub(r"\s+Page: [0-9]+ / [0-9]+\s+", "\n", text)
    text = re.sub(r"\s+Qualifications essentielles / Essential Qualifications\s+", "\n", text)
    text = re.sub(r"\s+Qualifications constituant un atout / Asset Qualifications\s+", "\n", text)
    text = re.sub(r"\n\n+", "\n\n", text)

    ignore_question = False
    answer_text_array = []
    question_text_array = []
    answer_text = []
    x = 0
    while "Question - Anglais / English:" in text:
        x += 1
        question_text = text.split("Question - Anglais / English:", 1)[1].split("Réponse du postulant", 1)[0]
        if "Complementary Answer:" in text:
            answer_text = "Réponse Complémentaire: / Complementary Answer:\n" + text.split("Complementary Answer:", 1)[1].split("Question - Français", 1)[0]
            answer_text_array.append(answer_text)
        for item in question_text_array:
            if fuzz.ratio(question_text, item) > 90:
                ignore_question = True
        if not ignore_question:
            question_text_array.append(question_text)
            ignore_question = False

        text = text.replace("Question - Anglais / English:" + question_text + "Réponse du postulant", "", 1)
        text = text.replace("Complementary Answer:" + answer_text + "Question - Français", "", 1)

    spacing_array = []

    for idx, question in enumerate(question_text_array):
        lookup_text = question
        spacing_array.append(lookup_text)

    for idx, answer in enumerate(answer_text_array):
        lookup_text = answer
        spacing_array.append(lookup_text)
    return spacing_array


def get_tika_text(pdf_file_path):
    fileData = parser.from_file(pdf_file_path)
    text = fileData['content']
    return text


def split_tika_text(tika_text):
    applicant_text_list = []
    applicant_list = tika_text.split("Liste des postulants / Applicant List", 1)[1].split("Page", 1)[0]
    applicant_list = applicant_list.split("\n\n")
    for idx, item in enumerate(applicant_list):
        applicant_list[idx] = item.strip()
        if item == "":
            del applicant_list[idx]

    main_text = tika_text.split("applicant starts on a new page.", 1)[1]
    for index, applicant_text in enumerate(applicant_list):
        if index == (len(applicant_list) - 1):
            temp_text = main_text.split(applicant_list[index], 1)[1].strip()
            applicant_text_list.append(temp_text)
        else:
            temp_text = main_text.split(applicant_list[index], 1)[1]
            temp_text = temp_text.split(applicant_list[index + 1], 1)[0]
            applicant_text_list.append(temp_text)

    return applicant_text_list


def get_first_page(item):
    html = item.to_html(index=False, header=False)
    document = HTML(string=html).render(stylesheets=[CSS(
        string='table, th, td {border: 1px solid black; border-collapse: collapse; font-size: 7px; vertical-align: middle;}')])
    return document


def clean_and_redact(data_frames, pdf_file_path, filename):
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
            spacing_array = get_spacing_array_of_tuples(text)
            pages += find_essential_details(
                data_frames[applicant_page_numbers[current_applicant]:], spacing_array)
        else:
            print("Processing Applicant: " + str(current_applicant + 1))
            text = applicant_text_array[current_applicant]
            spacing_array = get_spacing_array_of_tuples(text)
            pages += find_essential_details(
                data_frames[applicant_page_numbers[current_applicant]:applicant_page_numbers[current_applicant + 1]],
                spacing_array)
    document = get_first_page(data_frames[0])
    document.copy(pages).write_pdf('redacted/re' + filename)
    pass


def redact_applications():
    pd.set_option('display.max_colwidth', -1)
    count = 0
    if not os.path.isdir("redacted"):
        print("Creating folder redacted...")
        os.mkdir("redacted")

    directory = "sensitive"
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_file_path = os.path.join(directory, filename)
            df = tabula.read_pdf(pdf_file_path, options, pages="all", multiple_tables="true", guess=False,
                                 lattice="true")
            clean_and_redact(df, pdf_file_path, filename)

            continue
        else:
            continue

    return count

