import os
import re
import tempfile
from dateutil import parser as dateparser
import pdfkit
import tika
from tika import parser
from screendoor_app.settings import BASE_DIR


def extract_job_title(text):
    jobTitle = "N/A"

    if "Reference" in text:
        # Gets job title between 2 strings, Home and Reference.
        jobTitle = text.split('Home', 1)[1].split("Reference", 1)[0]
        jobTitle = " ".join(jobTitle.split())

    return jobTitle


def extract_who_can_apply(text):
    who_can_apply = "N/A"

    if "Who can apply:" in text:
        who_can_apply = text.split("Who can apply:", 1)[1].split(".", 1)[0]

    return who_can_apply


def extract_essential_block(text):
    essentialBlock = "N/A"

    # Every poster normally has "essential qualifications"
    # but not every poster has assets in the form of "other qualifications"
    # These if statements check both cases to extract the text block containing experience and education.

    if "(essential qualifications)" in text:
        if "If you possess any" in text:
            essentialBlock = text.split('(essential qualifications)', 1)[1].split("If you possess any", 1)[0]
        else:
            essentialBlock = \
                text.split('(essential qualifications)', 1)[1].split("The following will be applied / assessed", 1)[0]

    return essentialBlock


def extract_asset_block(text):
    assetBlock = "N/A"

    if "(other qualifications)" in text:
        assetBlock = text.split('(other qualifications)', 1)[1].split("The following will be ", 1)[0]

    return assetBlock


def extract_education(essential_block):
    education = "N/A"

    if "Degree equivalency\n" in essential_block:
        education = essential_block.split("Degree equivalency\n", 1)[0]
        education = education.lstrip()
        education = education.rstrip()

    return education


def extract_experience(essential_block):
    experience = "N/A"

    if "Degree equivalency\n" in essential_block:
        experience = essential_block.split("Degree equivalency\n", 1)[1]
        experience = experience.lstrip()
        experience = experience.rstrip()

    return experience


def extract_assets(asset_block):
    assets = asset_block
    assets = assets.lstrip()
    assets = assets.rstrip()
    return assets


def extract_salary_min(salary):
    salary_min = salary.split(" to ", 1)[0]
    salary_min = salary_min.replace("$", "")
    salary_min = salary_min.replace(",", "")
    return salary_min


def extract_salary_max(salary):
    salary_max = salary.split(" to ", 1)[1].split(" ")[0]
    salary_max = salary_max.replace("$", "")
    salary_max = salary_max.replace(",", "")

    return salary_max


def extract_classification(description):
    # Regex string that looks for the qualification level in  the form of two capital letters and two numbers
    # separated by a hyphen.
    classification = re.findall(r"([A-Z][A-Z][x-]\d\d)", description)[0]

    return classification


def extract_closing_date(item):
    # Strip the string and remove any leading or trailing spacing. Find text after colon. Ex. closing date: dd/mm/yy
    raw_date = item.strip().split(": ")[1]
    date = raw_date.rsplit(",", 1)[0]
    closing_date = dateparser.parse(date)

    return closing_date


def find_essential_details(text, position):
    from .models import Requirement

    reference_number = "N/A"
    selection_process_number = "N/A"
    closing_date = "N/A"
    spots_left = None
    description = "N/A"
    salary_min = 0
    salary_max = 0

    # Regex to remove lines starting with https and mailto

    text = re.sub(r'^https?://.*[\r\n]*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^mailto?:*[\r\n]*', '', text, flags=re.MULTILINE)
    text = text.strip("\n\n")

    job_title = extract_job_title(text)

    essential_block = extract_essential_block(text)

    asset_block = extract_asset_block(text)

    education = extract_education(essential_block)

    experience = extract_experience(essential_block)

    who_can_apply = extract_who_can_apply(text)

    assets = extract_assets(asset_block)

    parsing = False

    # A loop that extracts single line position fields like salary or reference number

    for item in text.split("\n"):

        if '$' in item:
            salary = item.strip()
            salary_min = extract_salary_min(salary)
            salary_max = extract_salary_max(salary)
            parsing = False
        if parsing:
            description = description + " " + item.strip()
        elif "Reference number" in item:
            reference_number = item.strip().split(": ")[1]
        elif "Selection process number" in item:
            selection_process_number = item.strip().split(": ")[1]
            parsing = True
        elif "Closing date" in item:
            closing_date = extract_closing_date(item)
        elif "Position:" in item or "Positions to be filled:" in item:
            spots_left = item.strip().split(": ")[1]

    description = description.replace('N/A  ', '', 1)
    classification = extract_classification(description)

    # Save all position info to position.

    position.date_closed = closing_date
    position.position_title = job_title
    position.num_positions = spots_left
    position.salary_min = salary_min
    position.salary_max = salary_max
    position.classification = classification
    position.description = description
    position.open_to = who_can_apply
    position.reference_number = reference_number
    position.selection_process_number = selection_process_number
    position.save()
    requirement_education = Requirement(position=position, requirement_type="educations", abbreviation="",
                                        description=education)
    requirement_experience = Requirement(position=position, requirement_type="experience", abbreviation="",
                                         description=experience)
    requirement_assets = Requirement(position=position, requirement_type="assets", abbreviation="", description=assets)
    requirement_education.save()
    requirement_experience.save()
    requirement_assets.save()

    return position


def parse_upload(position):
    if position.pdf.name:
        os.chdir("..")
        pdf_file_path = os.path.join(BASE_DIR, position.pdf.url)
        file_data = tika.parser.from_file(pdf_file_path, 'http://tika:9998/tika')
        job_poster_text = file_data['content']
        position = find_essential_details(job_poster_text, position)
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
