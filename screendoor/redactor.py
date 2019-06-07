import os

import numpy as np
import pandas as pd
import tabula
from pandas import options
from tika import parser
from weasyprint import HTML, CSS


def find_essential_details(list_of_data_frames, filename, count, pdf_file_path, string_array):
    length = len(list_of_data_frames)
    no_applicants_batch = 1
    # /////////////////////////////////////////////////////////////////////////

    list_of_data_frames = [item.replace(r'\r', ' ', regex=True) for item in list_of_data_frames]

    print("Reading file: " + filename)

    forbidden = []

    for idx, item in enumerate(list_of_data_frames):
        if item[0].dtype == np.float64 or item[0].dtype == np.int64:
            continue
        else:
            if item[0].str.contains("Nom de famille / Last Name:").any():
                count = count + 1
                no_applicants_batch = no_applicants_batch + 1
                print("Processing applicant: " + str(count))
                series = item.set_index(0)[1]
                forbidden.append(series["Nom de famille / Last Name:"])
                forbidden.append(series["No SRFP / PSRS no:"])
                series["Nom de famille / Last Name:"] = "REDACTED"
                series["Prénom / First Name:"] = "REDACTED"
                series["Initiales / Initials:"] = "REDACTED"
                series["No SRFP / PSRS no:"] = "REDACTED"
                list_of_data_frames[idx] = pd.DataFrame({0: series.index, 1: series.values})

            elif item[0].str.contains("Courriel / E-mail:").any():
                series = item.set_index(0)[1]
                forbidden.append(series["Courriel / E-mail:"])
                forbidden.append(series["Adresse / Address:"])
                forbidden.append(series["Téléphone / Telephone:"])
                series["Adresse / Address:"] = "REDACTED"
                series["Courriel / E-mail:"] = "REDACTED"
                series["Téléphone / Telephone:"] = "REDACTED"
                list_of_data_frames[idx] = pd.DataFrame({0: series.index, 1: series.values})
            elif item[0].str.contains("Adresse / Address:").any():
                series = item.set_index(0)[1]
                series["Adresse / Address:"] = "REDACTED"
                list_of_data_frames[idx] = pd.DataFrame({0: series.index, 1: series.values})

    # /////////////////////////////////////////////////////////////////////////

    documents = []
    print("Writing to html and appending to redacted pdf")
    print("This may take a while...")
    # //////////////////////// Li's html printing Thang ////////////////////////////////
    no_applicants_total = 1
    deletion = False
    for idx, item in enumerate(list_of_data_frames):

        if str(item.shape) == "(1, 1)":
            for string in string_array:
                if item.iat[0, 0].replace(" ", "").startswith(string):
                    print("Writing Applicant: " + str(no_applicants_total))
                    no_applicants_total = no_applicants_total + 1
                    print(item)
                    deletion = True

        if not (item[0].dtype == np.float64 or item[0].dtype == np.int64):
            if item[0].str.contains("Nom de famille / Last Name:").any():
                deletion = False

        if not deletion:
            html = item.to_html(index=False, header=False)
            documents.append(
                HTML(string=html).render(stylesheets=[CSS(string='table, tr, td {border: 1px solid black;}')]))

    pages = []

    for document in documents:
        for page in document.pages:
            pages.append(page)

    documents[0].copy(pages).write_pdf('redacted/re' + filename)
    print("TOTAL RESUMES REDACTED: " + str(no_applicants_total))
    print("TOTAL APPLICANTS: " + str(no_applicants_batch))

    return count


def get_resume_starter_string(pdf_file_path):
    string_array = []

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

    print(*string_array, sep='\n')
    return string_array


def parse_applications():
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
            df = tabula.read_pdf(pdf_file_path, options, pages="all", multiple_tables="true", lattice="true")
            string_array = get_resume_starter_string(pdf_file_path)
            count = find_essential_details(df, filename, count, pdf_file_path, string_array)
            continue
        else:
            continue

    return count


applicant_count = parse_applications()
print("Total number of applicants processed: " + str(applicant_count))
