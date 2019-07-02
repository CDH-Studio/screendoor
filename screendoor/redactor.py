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


def check_if_table_valid(table):
    # Checks if the table is a dataframe, not empty, and isn't None.
    return (isinstance(table, pd.DataFrame)) and (not table.empty) and (table is not None)


def correct_split_item(tables):
    # Corrects splits between tables. (Not including splits between questions or educations)
    for index, item in enumerate(tables):

        if check_if_table_valid(item):
            item = item.applymap(str)

            if ((index + 1) != len(tables)) and not str(item.shape) == "(1, 1)":
                item2 = tables[index + 1]
                item2 = item2.applymap(str)

                if item2.empty:
                    if (index + 2) != len(tables):
                        item2 = tables[index + 2]

                if check_if_table_valid(item2):
                    if "NaN" in item2.iloc[0, 0]:
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


def clean_data(x):


    x = re.sub(r'\r', 'abcdefg', x)
    x = re.sub(r'\n', ' ', x)
    return x


def find_essential_details(list_of_data_frames, filename, count, pdf_file_path, string_array):
    no_applicants_batch = 1
    list_of_data_frames = correct_split_item(list_of_data_frames)

    print("Reading file: " + filename)

    for idx, item in enumerate(list_of_data_frames):
        if item is None or item[0].dtype == np.float64 or item[0].dtype == np.int64:
            continue
        else:
            item = item.applymap(str)
            item = item.applymap(clean_data)

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
                                string='table, th, td {border: 1px solid black; border-collapse: collapse;  vertical-align: middle;}')]))

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
    array1 = text.split("Curriculum vitae / Résumé\n")
    string_array = []
    for idx, item in enumerate(array1):
        item = item.replace("\n", "")
        item = item.replace("\t", " ")
        item = item.strip()
        item = " ".join(item.split(" ", 2)[:2])
        item = item.replace(" ", "")
        string_array.append(item)

    return string_array


def redact_applications():
    print("Starting Redactor...")

    pd.set_option('display.max_colwidth', -1)
    count = 0
    if not os.path.isdir("redacted"):
        print("Creating folder redacted...")
        os.mkdir("redacted")

    directory = "sensitive"
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_file_path = os.path.join(directory, filename)
            df = tabula.read_pdf(pdf_file_path, options, pages="all", multiple_tables="true",
                                 lattice="true")
            string_array = get_resume_starter_string(pdf_file_path)
            count = find_essential_details(df, filename, count, pdf_file_path, string_array)
            continue
        else:
            continue

    return count
