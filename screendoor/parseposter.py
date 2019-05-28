import os
import re
import tempfile
from dateutil import parser as dateparser
import pdfkit
import tika
from tika import parser
from screendoor_app.settings import BASE_DIR


def print_information(jobTitle, closingDate, spotsLeft, salaryMin, salaryMax, classification, description,
                      whoCanApply, referenceNumber, selectionProcessNumber, url_ref, pdf, education, experience,
                      assets):
    print("Job Title : " + jobTitle)
    print("Closing Date : " + closingDate)
    print("Available Positions : " + str(spotsLeft))
    print("Salary Min : " + salaryMin)
    print("Salary Max : " + salaryMax)
    print("Classification : " + classification)
    print("Description : " + description)
    print("Who Can Apply : " + whoCanApply)
    print("Reference Number : " + referenceNumber)
    print("Selection Process Number : " + selectionProcessNumber)

    print("/////////////////  Education  ///////////////// \n" + education + "\n")
    print("/////////////////  Experience  ///////////////// \n" + experience + "\n")
    print("/////////////////  Assets  ///////////////// \n" + assets + "\n")

    return


def extract_job_title(text):
    jobTitle = "N/A"

    if "Reference" in text:
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

    if "(essential qualifications)" in text:
        if "If you possess any" in text:
            essentialBlock = text.split('(essential qualifications)', 1)[1].split("If you possess any", 1)[0]
        else:
            essentialBlock = text.split('(essential qualifications)', 1)[1].split("The following will be applied / assessed", 1)[0]

    return essentialBlock


def extract_asset_block(text):
    assetBlock = "N/A"

    if "(other qualifications)" in text:
        assetBlock = text.split('(other qualifications)', 1)[1].split("The following will be ", 1)[0]

    return assetBlock


def extract_education(essentialBlock):
    education = "N/A"

    if "Degree equivalency\n" in essentialBlock:
        education = essentialBlock.split("Degree equivalency\n", 1)[0]
        education = education.lstrip()
        education = education.rstrip()

    return education


def extract_experience(essentialBlock):
    experience = "N/A"

    if "Degree equivalency\n" in essentialBlock:
        experience = essentialBlock.split("Degree equivalency\n", 1)[1]
        experience = experience.lstrip()
        experience = experience.rstrip()

    return experience


def extract_Assets(assetBlock):
    assets = "N/A"

    assets = assetBlock
    assets = assets.lstrip()
    assets = assets.rstrip()
    return assets


def find_essential_details(text, path, position):
    from .models import Requirement

    reference_number = "N/A"
    selection_process_number = "N/A"
    who_can_apply = "N/A"
    closing_date = "N/A"
    spots_left = None
    salary = "N/A"
    description = "N/A"
    salary_min = 0
    salary_max = 0

    text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^mailto?:*[\r\n]*', '', text, flags=re.MULTILINE)
    text = text.strip("\n\n")

    job_title = extract_job_title(text)

    essential_block = extract_essential_block(text)

    asset_block = extract_asset_block(text)

    education = extract_education(essential_block)

    experience = extract_experience(essential_block)

    who_can_apply = extract_who_can_apply(text)

    assets = extract_Assets(asset_block)

    parsing = False
    for item in text.split("\n"):

        if '$' in item:
            salary = item.strip()
            salary_min = salary.split(" to ", 1)[0]
            salary_max = salary.split(" to ", 1)[1].split(" ")[0]
            parsing = False
        if parsing:
            description = description + " " + item.strip()
        elif "Reference number" in item:
            reference_number = item.strip().split(": ")[1]
        elif "Selection process number" in item:
            selection_process_number = item.strip().split(": ")[1]
            parsing = True
        elif "Closing date" in item:
            closing_date = item.strip().split(": ")[1]
        elif "Position:" in item or "Positions to be filled:" in item:
            spots_left = item.strip().split(": ")[1]

    description = description.replace('N/A  ', '', 1)
    classification = re.findall(r"([A-Z][A-Z][x-]\d\d)", description)[0]

    date = closing_date.rsplit(",", 1)[0]
    timezone = closing_date.rsplit(",", 1)[1]  # TODO Need to add timezone
    position.date_closed = dateparser.parse(date)

    position.position_title = job_title
    position.num_positions = spots_left

    salary_min = salary_min.replace("$", "")
    salary_min = salary_min.replace(",", "")
    salary_max = salary_max.replace("$", "")
    salary_max = salary_max.replace(",", "")

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

    print_information(job_title, closing_date, spots_left, salary_min, salary_max, classification, description,
                      who_can_apply, reference_number,
                      selection_process_number, position.url_ref, position.pdf, education, experience, assets)

    return position


def parse_upload(position):
    if position.pdf.name:
        os.chdir("..")
        pdf_file_path = os.path.join(BASE_DIR, position.pdf.url)
        file_data = tika.parser.from_file(pdf_file_path, 'http://tika:9998/tika')
        job_poster_text = file_data['content']
        position = find_essential_details(job_poster_text, pdf_file_path, position)
    else:
        url = position.url_ref

        temp = tempfile.NamedTemporaryFile()
        pdf_file_path =  temp.name

        try:
            pdfkit.from_url(str(url), str(pdf_file_path))
        except:
            pass
        file_data = tika.parser.from_file(pdf_file_path, 'http://tika:9998/tika')
        job_poster_text = file_data['content']
        position = find_essential_details(job_poster_text, pdf_file_path, position)

    return position
