import os

import pandas as pd
import tabula
from pandas import options
from weasyprint import HTML, CSS


def find_essential_details(list_of_data_frames, filename):
    # /////////////////////////////////////////////////////////////////////////

    list_of_data_frames = [item.replace(r'\r', ' ', regex=True) for item in list_of_data_frames]

    series1 = list_of_data_frames[1].set_index(0)[1]

    series1["Nom de famille / Last Name:"] = "REDACTED"
    series1["Prénom / First Name:"] = "REDACTED"
    series1["Initiales / Initials:"] = "REDACTED"
    series1["No SRFP / PSRS no:"] = "REDACTED"

    list_of_data_frames[1] = pd.DataFrame({'key': series1.index, 'value': series1.values})

    list_of_data_frames[1].to_html()

    # /////////////////////////////////////////////////////////////////////////

    series3 = list_of_data_frames[3].set_index(0)[1]

    series3["Adresse / Address:"] = "REDACTED"
    series3["Courriel / E-mail:"] = "REDACTED"
    series3["Téléphone / Telephone:"] = "REDACTED"

    list_of_data_frames[3] = pd.DataFrame({'key': series3.index, 'value': series3.values})

    # /////////////////////////////////////////////////////////////////////////

    series5 = list_of_data_frames[5].set_index(0)[1]
    series5["Adresse / Address:"] = "REDACTED"

    list_of_data_frames[5] = pd.DataFrame({'key': series5.index, 'value': series5.values})

    # /////////////////////////////////////////////////////////////////////////

    documents = []

    for item in list_of_data_frames:
        if str(item.shape) == "(1, 1)":
            if len(item.iat[0, 0]) > 2000:
                continue
        html = item.to_html(index=False, header=False)
        documents.append(HTML(string=html).render(stylesheets=[CSS(string='table, tr, td {border: 1px solid black;}')]))

    pages = []

    for document in documents:
        for page in document.pages:
            pages.append(page)

    documents[0].copy(pages).write_pdf('redacted/re' + filename)

    pass


def parse_application():

    pd.set_option('display.max_colwidth', -1)

    if not os.path.isdir("redacted"):
        os.mkdir("redacted")

    directory = "sensitive"

    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_file_path = os.path.join(directory, filename)
            df = tabula.read_pdf(pdf_file_path, options, pages="all", multiple_tables="true", lattice="true")
            find_essential_details(df, filename)
            continue
        else:
            continue

    pass


parse_application()
