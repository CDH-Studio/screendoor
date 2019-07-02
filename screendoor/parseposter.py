# ////////////////////////////////////////START IMPORTS//////////////////////////////////
import os
import re

import tika
from dateutil import parser as dateparser
from selenium.webdriver import DesiredCapabilities
from tika import parser

from .models import Requirement
from .uservisibletext import ErrorMessages


# ////////////////////////////////////////END IMPORTS////////////////////////////////////


def text_between(start_string, end_string, text):
    # Effectively returns the string between the first occurrence of start_string and end_string in text
    extracted_text = text.split(start_string, 1)[1].split(end_string, 1)[0]

    return extracted_text


def extract_essential_block(text):
    essential_block = ""

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
    asset_block = ""

    # Some posters have an assets section found between other qualifications and the statement "The following will be"

    if "(other qualifications)" in text:
        asset_block = text_between('(other qualifications)', "The following will be ", text)

    return asset_block


def extract_education(essential_block):
    education = ""

    # Due to the fact that the stylistics of the statement "EDUCATION: in the
    # essential requirements section vary, there is an array called titles that
    # stores all possible variations. They are all lower case since the statement is processed in lower case, to prevent
    # unnecessary checks. Degree equivalency is a statement that separates education and experience.

    titles = ["education", "education:"]
    first_word = essential_block.split(" ", 1)[0]
    first_word_lower = first_word.lower()
    first_word_lower = first_word_lower.replace(" ", "")
    if "Degree equivalency\n" in essential_block:
        for title in titles:
            if first_word_lower.__contains__(title):
                education = text_between(first_word, "Degree equivalency", essential_block)
                education = education.lstrip()
                education = education.rstrip()
        if education == "":
            education = essential_block.split("Degree equivalency\n", 1)[0]
            education = education.lstrip()
            education = education.rstrip()

    education = scrub_hard_returns(education)

    return education


def extract_experience(essential_block):
    experience = ""

    # Same deal as the extract_education

    titles = ["experience", "experience:", "experiences:"]
    for item in essential_block.split("\n"):
        item_lower = item.lower()
        item_lower = item_lower.replace(" ", "")
        if "Degree equivalency\n" in essential_block:
            for title in titles:
                if title == item_lower:
                    experience = text_between(item, "Degree equivalency", essential_block)
                    experience = experience.lstrip()
                    experience = experience.rstrip()
            if experience == "":
                experience = essential_block.split("Degree equivalency\n", 1)[1]
                experience = experience.lstrip()
                experience = experience.rstrip()

    experience = scrub_hard_returns(experience)

    return experience


def extract_assets(asset_block):
    assets = asset_block

    # scrub out the phrase degree equivalency in asset block and return it essentially.

    if "Degree equivalency\n" in assets:
        assets = assets.replace("Degree equivalency\n", "")
    assets = assets.lstrip()
    assets = assets.rstrip()

    assets = scrub_hard_returns(assets)

    return assets


def extract_job_title(text):
    job_title = ""

    # Title can be found between the phrases "Home" and "reference"

    if "Reference" in text:
        # Gets job title between 2 strings, Home and Reference.
        job_title = text_between('Home', "Reference", text)
        job_title = " ".join(job_title.split())

    return scrub_extra_whitespace(job_title)


def extract_who_can_apply(text):
    who_can_apply = ""

    # Who can apply is found right after string "Who can apply:"

    if "Who can apply:" in text:
        who_can_apply = text_between("Who can apply:", ".", text)
    return scrub_extra_whitespace(who_can_apply)


def extract_salary_min(salary):
    # Salary normally looks like ???$ to ???$ where ??? is an amount.
    # Use the statement " to " to separate minimum and maximum salary values.
    # Scrub out $ and ,

    salary_min = salary.split(" to ", 1)[0]
    salary_min = salary_min.replace("$", "")
    salary_min = salary_min.replace(",", "")
    return salary_min


def extract_salary_max(salary):
    # Same deal as extract_salary_min

    salary_max = text_between(" to ", " ", salary)
    salary_max = salary_max.replace("$", "")
    salary_max = salary_max.replace(",", "")

    return salary_max


def extract_classification(description):
    # Regex string that looks for the qualification level in  the form of two capital letters and two numbers
    # separated by a hyphen.
    classification = ""
    if re.search(r"([A-Z][A-Z][x-]\d\d)", description):
        classification = re.findall(r"([A-Z][A-Z][x-]\d\d)", description)[0]

    return classification


def extract_closing_date(item):
    # Strip the string and remove any leading or trailing spacing. Find text after colon. Ex. closing date: dd/mm/yy
    raw_date = item.strip().split(": ")[1]
    date = raw_date.rsplit(",", 1)[0]
    closing_date = dateparser.parse(date)

    return closing_date


# Removes any newlines and double spaces caused by other parsing rules.
def scrub_extra_whitespace(item):
    return str(item).replace('\n', '').replace('  ', ' ')


def scrub_entry(text):
    # Scrubs out useless text
    text = text.strip()

    if re.search(r"\w+[:]", text):
        text = re.sub(r"\w+[:]", "", text)

    for item in text.split("\n"):

        if item.find("* Recent") != -1:
            text = text.split("* Significant", 1)[0]
            break
        elif item.find("* Significant") != -1:
            text = text.split("* Significant", 1)[0]
            break
        elif item.find("* Management") != -1:
            text = text.split("* Management", 1)[0]
            break

    return text


def scrub_hard_returns(text):
    # Removes extra spaces and newlines in sentences.

    # Fancy Regex that just removes newlines within sentences

    text = re.sub(r"(?<![.;])\n", " ", text)

    # Adds a newline after end of every sentence.

    text = text.replace("; ", ";\n")
    text = text.replace(". ", ".\n")

    text = re.sub(r'(\d+\.\s)', '', text, flags=re.MULTILINE)

    return text


def scrub_raw_text(pdf_poster_text):
    # Removes lines starting with https or mailto

    pdf_poster_text = re.sub(r"^https?://.*[\r\n]*", '', pdf_poster_text, flags=re.MULTILINE)
    pdf_poster_text = re.sub(r"^mailto?:*[\r\n]*", '', pdf_poster_text, flags=re.MULTILINE)

    # Removes lines starting with a date (This normally infers a footer extracted by tika

    for item in pdf_poster_text.split("\n"):

        if re.match('^\d{1,2}/\d{1,2}/\d{4}', item):
            pdf_poster_text = pdf_poster_text.replace(item, "")

        item = re.sub(' +', ' ', item)

    # Removes consecutive newlines

    pdf_poster_text = re.sub(r'\n\s*\n', '\n', pdf_poster_text)

    return pdf_poster_text


def generate_requirements(text, position, requirement_type,
                          requirement_abbreviation):
    text = scrub_entry(text)

    requirement_list = []
    x = 1
    lines = re.split('(?i)[;.]\n(?!or|and|and/or|or/and)', text)
    for item in lines:
        if item != "" and not item.lower().__contains__("incumbents"):
            item = scrub_extra_whitespace(item.strip())
            if not re.match(r"[*]", item):
                item.replace("\n", "")
                requirement_list.append(
                    Requirement(position=position,
                                requirement_type=requirement_type,
                                abbreviation=requirement_abbreviation + str(x),
                                description=item))
                x = x + 1
    return requirement_list


def save_requirement_lists(list1, list2, list3):
    # saves the lists of requirements

    mega_list = [list1, list2, list3]

    for req_list in mega_list:
        for item in req_list:
            item.save()
    return


def assign_single_line_values(position, pdf_poster_text):
    is_description_parsing = False

    # A loop that extracts single line position fields like salary or reference number. Also extracts description.

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

    return position


def find_essential_details(pdf_poster_text, position):
    # The mother of all methods, find_essential_details uses all the other methods to parse the job poster.

    pdf_poster_text = scrub_raw_text(pdf_poster_text)

    position.position_title = extract_job_title(pdf_poster_text)

    position.open_to = extract_who_can_apply(pdf_poster_text)

    essential_block = extract_essential_block(pdf_poster_text)

    asset_block = extract_asset_block(pdf_poster_text)

    requirement_education = extract_education(essential_block)

    requirement_experience = extract_experience(essential_block)

    requirement_assets = extract_assets(asset_block)

    position = assign_single_line_values(position, pdf_poster_text)

    position.save()

    education_reqs = generate_requirements(requirement_education, position,
                                           "Education", "ED")
    experience_reqs = generate_requirements(requirement_experience, position,
                                            "Experience", "EXP")
    asset_experience_reqs = generate_requirements(requirement_assets, position,
                                                  "Asset", "AEXP")
    save_requirement_lists(education_reqs, experience_reqs,
                           asset_experience_reqs)

    dictionary = {
        'position': position
    }

    return dictionary


def get_from_url():
    import json
    from selenium import webdriver

    driver = webdriver.Remote(
        command_executor='4444:4444',
        desired_capabilities=DesiredCapabilities.FIREFOX,
    )


def parse_upload(position):
    # checking for the existence of the pdf upload. If true, convert uploaded pdf into text
    # using tika and process using find_essential_details method. If false, process url.
    get_from_url()
    if position.pdf.name:
        os.chdir("..")
        file_data = tika.parser.from_buffer(position.pdf, 'http://tika:9998/tika')
        job_poster_text = file_data['content']
        if "Selection process number:" in job_poster_text:
            return find_essential_details(job_poster_text, position)
        else:
            return {'errors': ErrorMessages.incorrect_pdf_file}
    elif position.url_ref:

        return {'errors': ErrorMessages.url_upload_not_supported_yet}
