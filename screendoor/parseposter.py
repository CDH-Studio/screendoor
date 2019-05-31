# ////////////////////////////////////////START IMPORTS//////////////////////////////////
import os
import re
import tempfile

import nltk
import pdfkit
import tika
from dateutil import parser as dateparser
from tika import parser

from screendoor_app.settings import BASE_DIR
from .models import Requirement


# ////////////////////////////////////////END IMPORTS////////////////////////////////////


def text_between(start_string, end_string, text):
    # Effectively returns the string between the first occurrence of start_string and end_string in text
    extracted_text = text.split(start_string, 1)[1].split(end_string, 1)[0]

    return extracted_text


def extract_essential_block(text):
    essential_block = "N/A"

    # Every poster normally has "essential qualifications"
    # but not every poster has assets in the form of "other qualifications"
    # These if statements check both cases to extract the text block containing experience and education.

    if "(essential qualifications)" in text:
        if "If you possess any" in text:
            essential_block = text_between('(essential qualifications)', "If you possess any", text)

        else:
            essential_block = text_between('(essential qualifications)', "The following will be applied / assessed",
                                           text)

    return essential_block


def extract_asset_block(text):
    asset_block = "N/A"

    if "(other qualifications)" in text:
        asset_block = text_between('(other qualifications)', "The following will be ", text)

    return asset_block


def extract_education(essential_block, position):
    education = "N/A"
    titles = ["education", "education ", "education:", "education: "]
    for item in essential_block.split("\n"):
        item_lower = item.lower()
        if "Degree equivalency\n" in essential_block:
            for title in titles:
                if title == item_lower:
                    education = text_between(item, "Degree equivalency", essential_block)
                    education = education.lstrip()
                    education = education.rstrip()
            if education == "N/A":
                education = essential_block.split("Degree equivalency\n", 1)[0]
                education = education.lstrip()
                education = education.rstrip()

    lines = nltk.sent_tokenize(education)

    education = scrub_hard_returns(education)

    return Requirement(position=position, requirement_type="Education", abbreviation="", description=education)


def extract_experience(essential_block, position):
    experience = "N/A"

    titles = ["experience", "experience ", "experience:", "experience: ", "experiences: ", "experiences:"]
    for item in essential_block.split("\n"):
        item_lower = item.lower()
        if "Degree equivalency\n" in essential_block:
            for title in titles:
                if title == item_lower:
                    experience = text_between(item, "Degree equivalency", essential_block)
                    experience = experience.lstrip()
                    experience = experience.rstrip()
            if experience == "N/A":
                experience = essential_block.split("Degree equivalency\n", 1)[1]
                experience = experience.lstrip()
                experience = experience.rstrip()

    experience = scrub_hard_returns(experience)

    return Requirement(position=position, requirement_type="Experience", abbreviation="", description=experience)


def extract_assets(asset_block, position):
    assets = asset_block

    if "Degree equivalency\n" in assets:
        assets = assets.replace("Degree equivalency\n", "")
    assets = assets.lstrip()
    assets = assets.rstrip()

    assets = scrub_hard_returns(assets)

    return Requirement(position=position, requirement_type="Assets", abbreviation="", description=assets)


def extract_job_title(text):
    job_title = "N/A"

    if "Reference" in text:
        # Gets job title between 2 strings, Home and Reference.
        job_title = text_between('Home', "Reference", text)
        job_title = " ".join(job_title.split())

    return job_title


def extract_who_can_apply(text):
    who_can_apply = "N/A"
    if "Who can apply:" in text:
        who_can_apply = text_between("Who can apply:", ".", text)
    return who_can_apply


def extract_salary_min(salary):
    salary_min = salary.split(" to ", 1)[0]
    salary_min = salary_min.replace("$", "")
    salary_min = salary_min.replace(",", "")
    return salary_min


def extract_salary_max(salary):
    salary_max = text_between(" to ", " ", salary)
    salary_max = salary_max.replace("$", "")
    salary_max = salary_max.replace(",", "")

    return salary_max


def extract_classification(description):
    # Regex string that looks for the qualification level in  the form of two capital letters and two numbers
    # separated by a hyphen.
    classification = "N/A"
    if re.search(r"([A-Z][A-Z][x-]\d\d)", description):
        classification = re.findall(r"([A-Z][A-Z][x-]\d\d)", description)[0]

    return classification


def extract_closing_date(item):
    # Strip the string and remove any leading or trailing spacing. Find text after colon. Ex. closing date: dd/mm/yy
    raw_date = item.strip().split(": ")[1]
    date = raw_date.rsplit(",", 1)[0]
    closing_date = dateparser.parse(date)

    return closing_date


def education_requirements_engine(text, position):
    education_requirement_list = []

    return education_requirement_list


def scrub_definitions(text):
    for item in text.split("\n"):
        if item.find("* Recent") != -1:
            text = text.split("* Significant", 1)[0]
            break
        if item.find("* Significant") != -1:
            text = text.split("* Significant", 1)[0]
            break
        elif item.find("* Management") != -1:
            text = text.split("* Management", 1)[0]
            break
    return text


def scrub_hard_returns(text):
    text = re.sub(r"(?<!\.|\;)\n", " ", text)

    text = text.replace("; ", ";\n")
    text = text.replace(". ", ".\n")
    text = text.replace(": ", ":\n")

    text = re.sub(r'(\d+\.\s)', '', text, flags=re.MULTILINE)

    return text


def scrub_raw_text(pdf_poster_text):
    pdf_poster_text = re.sub(r'^https?://.*[\r\n]*', '', pdf_poster_text, flags=re.MULTILINE)
    pdf_poster_text = re.sub(r'^mailto?:*[\r\n]*', '', pdf_poster_text, flags=re.MULTILINE)

    for item in pdf_poster_text.split("\n"):

        if re.match('^\d{1,2}/\d{1,2}/\d{4}', item):
            pdf_poster_text = pdf_poster_text.replace(item, "")

        item = re.sub(' +', ' ', item)

    pdf_poster_text = re.sub(r'\n\s*\n', '\n', pdf_poster_text)

    return pdf_poster_text


def experience_requirements_engine(text, position):
    text = scrub_definitions(text)

    experience_requirement_list = []
    x = 1
    for item in re.split('[\.;]+', text):
        if item != "":
            item.replace("\n", "")
            experience_requirement_list.append(
                Requirement(position=position, requirement_type= "Experience", abbreviation="EX" + str(x), description=item))
            x = x + 1
    return experience_requirement_list


def assets_requirements_engine(text, position):
    assets_requirement_list = []

    return assets_requirement_list


def save_requirement_lists(list1, list2, list3):
    uber_list = [list1, list2, list3]

    for req_list in uber_list:
        for item in req_list:
            item.save()

    return


def find_essential_details(pdf_poster_text, position):
    # Regex to remove lines starting with https and mailto

    pdf_poster_text = scrub_raw_text(pdf_poster_text)

    print(pdf_poster_text)

    position.position_title = extract_job_title(pdf_poster_text)

    essential_block = extract_essential_block(pdf_poster_text)

    asset_block = extract_asset_block(pdf_poster_text)

    requirement_education = extract_education(essential_block, position)

    requirement_experience = extract_experience(essential_block, position)

    position.open_to = extract_who_can_apply(pdf_poster_text)

    requirement_assets = extract_assets(asset_block, position)

    is_description_parsing = False

    # list1 = education_requirements_engine(requirement_education.description, position)
    # list2 = experience_requirements_engine(requirement_experience.description, position)
    # list3 = assets_requirements_engine(requirement_assets.description, position)

    # A loop that extracts single line position fields like salary or reference number

    for item in pdf_poster_text.split("\n"):

        if '$' in item:
            salary = item.strip()
            position.salary_min = extract_salary_min(salary)
            position.salary_max = extract_salary_max(salary)
            is_description_parsing = False
        if is_description_parsing:
            position.description = position.description + " " + item.strip()
        elif "Reference number" in item:
            position.reference_number = item.strip().split(": ")[1]
        elif "Selection process number" in item:
            position.selection_process_number = item.strip().split(": ")[1]
            is_description_parsing = True
        elif "Closing date" in item:
            position.date_closed = extract_closing_date(item)
        elif "Position:" in item or "Positions to be filled:" in item:
            position.num_positions = item.strip().split(": ")[1]

    position.description = position.description.replace('N/A  ', '', 1)
    position.classification = extract_classification(position.description)

    # Save all position info to position.
    position.save()

    requirement_education.save()
    requirement_experience.save()
    requirement_assets.save()
    # save_requirement_lists(list1, list2, list3)

    return position


def parse_upload(position):
    # checking for the existence of the pdf upload. If true, convert uploaded pdf into text
    # using tika and process using find_essential_details method. If false, process url.
    if position.pdf.name:
        os.chdir("..")
        pdf_file_path = os.path.join(BASE_DIR, position.pdf.url)
        file_data = tika.parser.from_file(pdf_file_path, 'http://tika:9998/tika')
        job_poster_text = file_data['content']
        if "Selection process number:" in job_poster_text:
            position = find_essential_details(job_poster_text, position)
        else:
            return None
    else:
        url = position.url_ref

        temp = tempfile.NamedTemporaryFile()
        pdf_file_path = temp.name

        try:
            pdfkit.from_url(str(url), str(pdf_file_path))
        except:
            pass

        file_data = tika.parser.from_file(pdf_file_path, 'http://tika:9998/tika')
        job_poster_text = file_data['content']
        position = find_essential_details(job_poster_text, position)

    return position
