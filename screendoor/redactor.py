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


def clean_question_data(x, spacing_array):
    if is_valid_cell(x):
        x = re.sub(r"\r", "\n", x)

        for item in spacing_array:
            if item[0] in x:
                x = x.replace(item[0], item[1] + "\n\n")

        x = re.sub(r'\n', 'jJio', x)

    return x


def is_question(item):
    first_column = item[item.columns[0]]

    if first_column.str.startswith("Question - Français").any():
        return True
    return False


def find_essential_details(list_of_data_frames, filename, count, string_array, spacing_array):
    no_applicants_batch = 1
    list_of_data_frames = split_complementary_answer(list_of_data_frames)
    print("Entering Loop")
    for idx, item in enumerate(list_of_data_frames):
        if item is None or item[0].dtype == np.float64 or item[0].dtype == np.int64:
            continue
        else:
            item = item.applymap(str)
            item = item.applymap(lambda x: clean_question_data(x, spacing_array))

            for field in forbidden:
                for index, row in item.iterrows():
                    found_string = item.iloc[index, 0]
                    ratio = fuzz.ratio(field, found_string)
                    if ratio > 70:
                        item.iloc[index, 1] = "REDACTED"

            list_of_data_frames[idx] = item

    documents = []
    print("Writing to html and appending to redacted pdf")
    print("This may take a while...")

    no_applicants_total = 1

    ignore = False
    for idx, item in enumerate(list_of_data_frames):
        if item is None or item[0].dtype == np.float64 or item[0].dtype == np.int64:
            continue
        if str(item.shape) == "(1, 1)":

            for string in string_array:
                if item.iat[0, 0].replace(" ", "").startswith(string):
                    ignore = True

        if item is not None:
            if not (item[0].dtype == np.float64 or item[0].dtype == np.int64):
                if item[0].str.contains("Nom de famille / Last Name:").any():
                    print("Writing Applicant: " + str(no_applicants_total))
                    no_applicants_total = no_applicants_total + 1
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

    documents[0].copy(pages).write_pdf('redacted/re' + filename)
    print("TOTAL RESUMES REDACTED: " + str(no_applicants_total))
    print("TOTAL APPLICANTS: " + str(no_applicants_batch))

    return count


def get_resume_starter_string(pdf_file_path):
    fileData = parser.from_file(pdf_file_path)
    text = fileData['content']
    spacing_array = get_spacing_array_of_tuples(text)
    array1 = text.split("Curriculum vitae / Résumé\n")
    string_array = []
    for idx, item in enumerate(array1):
        item = item.replace("\n", "")
        item = item.replace("\t", " ")
        item = item.strip()
        item = " ".join(item.split(" ", 2)[:2])
        item = item.replace(" ", "")
        string_array.append(item)

    return string_array, spacing_array


def get_spacing_array_of_tuples(text):
    # Page numbers cleaned out
    text = re.sub(r"\s+Page: [0-9]+ / [0-9]+\s+", "\n", text)
    text = re.sub(r"\s+Qualifications essentielles / Essential Qualifications\s+", "\n", text)
    text = re.sub(r"\s+Qualifications constituant un atout / Asset Qualifications\s+", "\n", text)
    text = re.sub(r"\n\n+", "\n\n", text)

    ignore_question = False
    answer_text_array = []
    question_text_array = []
    x = 0
    while "Question - Anglais / English:" in text:
        x += 1
        question_text = text.split("Question - Anglais / English:", 1)[1].split("Réponse du postulant", 1)[0]
        if "Complementary Answer:" in text:
            answer_text = text.split("Complementary Answer:", 1)[1].split("Question - Français", 1)[0]
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
        question_copy = question.strip()
        while "\n\n" in question_copy:
            after_space_comparison = question_copy.split("\n\n", 1)[1].replace("\n\n", "\n")
            after_space_actual = question_copy.split("\n\n", 1)[1]
            question_copy = question_copy.replace("\n\n", "", 1)
            spacing_array.append((after_space_comparison, after_space_actual))

    for idx, answer in enumerate(answer_text_array):
        answer_copy = answer.strip()
        while "\n\n" in answer_copy:
            after_space_comparison = answer_copy.split("\n\n", 1)[1].replace("\n\n", "\n")
            after_space_actual = answer_copy.split("\n\n", 1)[1]

            answer_copy = answer_copy.replace("\n\n", "", 1)
            spacing_array.append((after_space_comparison, after_space_actual))

    return spacing_array


def redact_applications():
    print("Starting redactor")

    pd.set_option('display.max_colwidth', -1)
    count = 0
    if not os.path.isdir("redacted"):
        print("Creating folder redacted...")
        os.mkdir("redacted")

    directory = "sensitive"
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_file_path = os.path.join(directory, filename)
            print("Reading document...")
            df = tabula.read_pdf(pdf_file_path, options, pages="all", multiple_tables="true", guess=False,
                                 lattice="true")
            print("Document read")
            arrays = get_resume_starter_string(pdf_file_path)
            print("Resume and Spacing Strings Identified")

            string_array = arrays[0]
            spacing_array = arrays[1]
            print("Beginning Analysis")
            count = find_essential_details(df, filename, count, string_array, spacing_array)
            continue
        else:
            continue

    return count


redact_applications()
