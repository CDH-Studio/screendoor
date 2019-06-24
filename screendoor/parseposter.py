# ////////////////////////////////////////START IMPORTS//////////////////////////////////
import os
import re

import tika

tika.TikaClientOnly = True
from dateutil import parser as dateparser
from fuzzywuzzy import fuzz, process
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


def clean_block(text):
    text = text.strip()
    # Remove number points like "2. "
    text = re.sub(r'(\d+\.\s)', '', text, flags=re.MULTILINE)

    return text


def extract_education(essential_block):
    education = ""

    split_by_line_breaks = essential_block.split("\n")

    for sentence1 in split_by_line_breaks:
        if fuzz.ratio("education:", sentence1.lower()) > 80:
            for sentence2 in split_by_line_breaks:
                if fuzz.ratio("Degree equivalency", sentence2.lower()) > 80:
                    education = text_between(sentence1, sentence2, essential_block)

    education = clean_block(education)

    return education


def extract_experience(essential_block):
    experience = ""
    split_by_line_breaks = essential_block.split("\n")

    for sentence1 in split_by_line_breaks:
        if fuzz.ratio("Degree equivalency", sentence1) > 80:
            experience = essential_block.split(sentence1, 1)[1]
        if fuzz.ratio("experience:", sentence1.lower()) > 80:
            experience = essential_block.split(sentence1, 1)[1]

    experience = clean_block(experience)

    return experience


def extract_assets(asset_block):
    assets = asset_block
    split_by_line_breaks = asset_block.split("\n")

    for sentence1 in split_by_line_breaks:
        if fuzz.ratio("Degree equivalency", sentence1) > 80:
            assets = assets.replace(sentence1, "\n")

    assets = clean_block(assets)

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


def clean_out_titles(text):
    if re.search(r"^[A-Z].+:$", text):
        text = re.sub(r"^[A-Z].+:$", "", text)
    return text


def save_requirement_lists(list1, list2, list3):
    # saves the lists of requirements

    mega_list = [list1, list2, list3]

    for req_list in mega_list:
        for item in req_list:
            item.save()
    return


# Removes any newlines and double spaces caused by other parsing rules.
def scrub_extra_whitespace(item):
    return str(item).replace('\n', ' ').replace('  ', ' ')


def scrub_requirement_block(requirement_block_text):
    requirement_block_text = requirement_block_text.strip()
    single_line_break_list = requirement_block_text.split("\n")

    for sentence in single_line_break_list:
        sentence = sentence.strip()
        if sentence.lower().startswith("definitions:") or sentence.lower().startswith("note:") or \
                sentence.lower().startswith("notes:") or "incumbents" in sentence.lower():
            requirement_block_text = requirement_block_text.split(sentence, 1)[0]
            requirement_block_text = clean_out_titles(requirement_block_text)

            return requirement_block_text

    for sentence in single_line_break_list:
        if re.search(r"^\** Recent", sentence):
            requirement_block_text = requirement_block_text.split(sentence, 1)[0]
            break
        elif re.search(r"^\** Significant", sentence):
            requirement_block_text = requirement_block_text.split(sentence, 1)[0]
            break
        elif re.search(r"^\** Management", sentence):
            requirement_block_text = requirement_block_text.split(sentence, 1)[0]
            break
        elif "defined as" in sentence:
            requirement_block_text = requirement_block_text.split(sentence, 1)[0]

    requirement_block_text = clean_out_titles(requirement_block_text)

    return requirement_block_text


def separate_requirements(requirement_block_text):
    requirement_list = re.split('[;.]\s*\n', requirement_block_text)

    for idx, item in enumerate(requirement_list):
        item = item.strip()
        if len(item) > 30 and ("or more of the following" in item.lower() or "common to all streams") in item.lower():
            if ":" in item:
                requirement_list.append(item.split(":", 1)[1])
                item = ""
                requirement_list[idx] = item
                continue
        if item.startswith("or") or item.startswith("and"):
            requirement_list[idx - 1] = requirement_list[idx - 1] + item
            item = ""
            requirement_list[idx] = item
            continue
        requirement_list[idx] = item

    return requirement_list


def generate_requirements(requirement_block_text, position, requirement_type,
                          requirement_abbreviation):
    requirement_block_text = scrub_requirement_block(requirement_block_text)
    requirement_model_list = []
    requirement_list = separate_requirements(requirement_block_text)
    x = 1
    for item in requirement_list:
        if item.strip() != "" and not item.lower().__contains__("incumbents"):
            item = scrub_extra_whitespace(item.strip())
            item.replace("\n", "")
            requirement_model_list.append(
                Requirement(position=position,
                            requirement_type=requirement_type,
                            abbreviation=requirement_abbreviation + str(x),
                            description=item))
            x = x + 1
    return requirement_model_list


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


def scrub_raw_text(pdf_poster_text):
    # Removes lines starting with https or mailto

    pdf_poster_text = re.sub(r"^https?://.*[\r\n]*", '', pdf_poster_text, flags=re.MULTILINE)
    pdf_poster_text = re.sub(r"^mailto?:*[\r\n]*", '', pdf_poster_text, flags=re.MULTILINE)

    # Removes lines starting with a date (This normally infers a footer extracted by tika
    split_new_lines_text = pdf_poster_text.split("\n")

    for idx, item in enumerate(split_new_lines_text):

        if re.match('^\d{1,2}/\d{1,2}/\d{4}', item):
            pdf_poster_text = pdf_poster_text.replace(item, "")

        split_new_lines_text[idx] = re.sub(' +', ' ', item)

    # Removes consecutive newlines

    pdf_poster_text = re.sub(r'\n\n+', '\n\n', pdf_poster_text)

    return pdf_poster_text


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


def parse_upload(position):
    # checking for the existence of the pdf upload. If true, convert uploaded pdf into text
    # using tika and process using find_essential_details method. If false, process url.

    if position.pdf.name:
        os.chdir("..")
        file_data = tika.parser.from_buffer(position.pdf, 'http://tika:9998/tika')
        job_poster_text = file_data['content']
        if "Selection process number:" in job_poster_text:
            return find_essential_details(job_poster_text, position)
        else:
            return {'errors': ErrorMessages.incorrect_pdf_file}
    elif position.url_ref:

        import json
        from selenium import webdriver

        appState = {
            "recentDestinations": [
                {
                    "id": "Save as PDF",
                    "origin": "local"
                }
            ],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }
        downloadPath = "code/screendoor"

        profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState),
                   'savefile.default_directory': downloadPath}

        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_experimental_option('prefs', profile)
        chrome_options.add_argument('--kiosk-printing')

        driver = webdriver.Chrome(chrome_options=chrome_options)

        driver.get('https://www.google.com/')
        driver.execute_script('window.print();')

        driver.quit()

        return {'errors': ErrorMessages.url_upload_not_supported_yet}
