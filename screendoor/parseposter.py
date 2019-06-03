# ////////////////////////////////////////START IMPORTS//////////////////////////////////
import os
import re
import tempfile

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

    # Some posters have an assets section found between other qualifications and the statement "The following will be"

    if "(other qualifications)" in text:
        asset_block = text_between('(other qualifications)', "The following will be ", text)

    return asset_block


def extract_education(essential_block, position):
    education = "N/A"

    # Due to the fact that the stylistics of the statement "EDUCATION: in the
    # essential requirements section vary, there is an array called titles that
    # stores all possible variations. They are all lower case since the statement is processed in lower case, to prevent
    # unnecessary checks. Degree equivalency is a statement that separates education and experience.

    titles = ["education", "education:"]
    first_word = essential_block.split(" ", 1)[0]
    print(first_word)
    first_word_lower = first_word.lower()
    first_word_lower = first_word_lower.replace(" ","")
    if "Degree equivalency\n" in essential_block:
        for title in titles:
            if first_word_lower.__contains__(title):
                education = text_between(first_word, "Degree equivalency", essential_block)
                education = education.lstrip()
                education = education.rstrip()
        if education == "N/A":
            education = essential_block.split("Degree equivalency\n", 1)[0]
            education = education.lstrip()
            education = education.rstrip()

    education = scrub_hard_returns(education)

    return Requirement(position=position, requirement_type="Education", abbreviation="CONTENT", description=education)


def extract_experience(essential_block, position):
    experience = "N/A"

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
            if experience == "N/A":
                experience = essential_block.split("Degree equivalency\n", 1)[1]
                experience = experience.lstrip()
                experience = experience.rstrip()

    experience = scrub_hard_returns(experience)

    return Requirement(position=position, requirement_type="Experience", abbreviation="CONTENT", description=experience)


def extract_assets(asset_block, position):
    assets = asset_block

    # scrub out the phrase degree equivalency in asset block and return it essentially.

    if "Degree equivalency\n" in assets:
        assets = assets.replace("Degree equivalency\n", "")
    assets = assets.lstrip()
    assets = assets.rstrip()

    assets = scrub_hard_returns(assets)

    return Requirement(position=position, requirement_type="Assets", abbreviation="CONTENT", description=assets)


def extract_job_title(text):
    job_title = "N/A"

    # Title can be found between the phrases "Home" and "reference"

    if "Reference" in text:
        # Gets job title between 2 strings, Home and Reference.
        job_title = text_between('Home', "Reference", text)
        job_title = " ".join(job_title.split())

    return job_title


def extract_who_can_apply(text):
    who_can_apply = "N/A"

    # Who can apply is found right after string "Who can apply:"

    if "Who can apply:" in text:
        who_can_apply = text_between("Who can apply:", ".", text)
    return who_can_apply


def extract_salary_min(salary):
    # Salary normally looks like ???$ to ???$ where ??? is an amount.
    # Use the statment " to " to separate minimum and maximum salary values.
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


def scrub_definitions(text):
    # Scrubs out definitions sometimes found at the bottom of the experience section.

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


def experience_requirements_engine(text, position):
    # Generates EX1, EX2, etc.

    text = scrub_definitions(text)

    experience_requirement_list = []
    x = 1
    for item in re.split('(?<!\d)[;.]|[;.](?!\d)', text):
        if item != "":
            item.replace("\n", "")
            experience_requirement_list.append(
                Requirement(position=position, requirement_type="Experience", abbreviation="EX" + str(x),
                            description=item))
            x = x + 1
    return experience_requirement_list


def education_requirements_engine(text, position):
    # Generates the ED1, ED2, etc.

    text = scrub_definitions(text)

    education_requirement_list = []
    x = 1
    for item in re.split('[.;]+', text):
        if item != "":
            item.replace("\n", "")
            education_requirement_list.append(
                Requirement(position=position, requirement_type="Education", abbreviation="ED" + str(x),
                            description=item))
            x = x + 1
    return education_requirement_list


def assets_requirements_engine(text, position):
    # Generates A01, AO2, etc.

    text = scrub_definitions(text)

    assets_requirement_list = []
    x = 1
    for item in re.split('[.;]+', text):
        if item != "":
            item.replace("\n", "")
            assets_requirement_list.append(
                Requirement(position=position, requirement_type="Asset", abbreviation="A" + str(x),
                            description=item))
            x = x + 1
    return assets_requirement_list


def save_requirement_lists(list1, list2, list3):
    # saves the lists of requirements generated by the engines

    mega_list = [list1, list2, list3]

    for req_list in mega_list:
        for item in req_list:
            item.save()
            print(item)

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

    requirement_education = extract_education(essential_block, position)

    requirement_experience = extract_experience(essential_block, position)

    requirement_assets = extract_assets(asset_block, position)

    position = assign_single_line_values(position, pdf_poster_text)

    position.save()
    requirement_education.save()
    requirement_experience.save()
    requirement_assets.save()

    list1 = education_requirements_engine(requirement_education.description, position)
    list2 = experience_requirements_engine(requirement_experience.description, position)
    list3 = assets_requirements_engine(requirement_assets.description, position)
    save_requirement_lists(list1, list2, list3)

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
