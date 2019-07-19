# ////////////////////////////////////////START IMPORTS//////////////////////////////////
import os
import re
import time

import tika
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from weasyprint import HTML

tika.TikaClientOnly = True
from dateutil import parser as dateparser
from fuzzywuzzy import fuzz
from tika import parser

from .models import Requirement
from .uservisibletext import ErrorMessages


# ////////////////////////////////////////END IMPORTS////////////////////////////////////


def text_between(start_string, end_string, text):
    # Effectively returns the string between the first occurrence of start_string and end_string in text
    extracted_text = text.split(start_string, 1)[1].split(end_string, 1)[0]

    return extracted_text


def clean_block(text):
    text = text.strip()
    # Remove number points like "2. "
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)

    return text


def extract_education(essential_block):
    education = ""

    split_by_line_breaks = essential_block.split("\n")

    for sentence1 in split_by_line_breaks:
        if fuzz.ratio("Degree equivalency", sentence1.lower()) > 80:
            education = essential_block.rsplit(sentence1)[0]

    education = clean_block(education)

    return education


def extract_experience(essential_block):
    experience = ""
    split_by_line_breaks = essential_block.split("\n")

    for sentence1 in split_by_line_breaks:
        if fuzz.ratio("Degree equivalency", sentence1) > 80:
            experience = essential_block.split(sentence1, 1)[1]

    experience = clean_block(experience)

    return experience


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
    if "//" in salary:
        return 0
    decimal_numbers = re.findall("\d+\.\d+", salary)
    if len(decimal_numbers) > 0:
        salary_min = float(decimal_numbers[0])
    else:
        salary_min = salary.split(" to ", 1)[0]
        salary_min = salary_min.replace("$", "")
        salary_min = salary_min.replace(",", "")
    return salary_min


def extract_salary_max(salary):
    # Same deal as extract_salary_min
    if "//" in salary:
        return 0
    decimal_numbers = re.findall("\d+\.\d+", salary)
    if len(decimal_numbers) > 0:
        salary_max = float(decimal_numbers[1])
    else:
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


def find_and_remove(pattern, text):
    if re.search(pattern, text):
        text = re.sub(pattern, "", text)

    return text


def clean_out_titles(text, header_pattern):
    text = re.sub(header_pattern, "", text, re.MULTILINE)

    return text


# Removes any newlines and double spaces caused by other parsing rules.
def scrub_extra_whitespace(item):
    item.strip()
    return str(item).replace('\n', ' ').replace('  ', ' ')


def extract_text_blocks(pdf_poster_text):
    # Every poster normally has "essential qualifications"
    # but not every poster has assets in the form of "other qualifications"
    # These if statements check both cases to extract the text block containing experience and education.
    essential_block = ""

    if "(essential qualifications)" in pdf_poster_text:
        if "If you possess any" in pdf_poster_text:
            essential_block = text_between('(essential qualifications)', "If you possess any", pdf_poster_text)

        else:
            essential_block = text_between('(essential qualifications)', "The following will be applied / assessed",
                                           pdf_poster_text)

    requirement_education = extract_education(essential_block)

    requirement_experience = extract_experience(essential_block)

    requirement_assets = extract_asset(pdf_poster_text)

    return requirement_education, requirement_experience, requirement_assets


def extract_req_list(pdf_poster_text, position):
    # Extracts text blocks like education, experience and assets
    text_blocks = extract_text_blocks(pdf_poster_text)

    education_reqs = generate_requirements(text_blocks[0], position,
                                           "Education", "ED")
    experience_reqs = generate_requirements(text_blocks[1], position,
                                            "Experience", "EXP")
    asset_experience_reqs = generate_requirements(text_blocks[2], position,
                                                  "Asset", "AEXP")

    return education_reqs + experience_reqs + asset_experience_reqs


def extract_asset(text):
    asset_block = ""

    # Some posters have an assets section found between other qualifications and the statement "The following will be"

    if "(other qualifications)" in text:
        asset_block = text_between('(other qualifications)', "The following will be ", text)
    # elif "(essential for the job)" in text:
    # asset_block = text_between('(essential for the job)', "The following may be ", text)

    split_by_line_breaks = asset_block.split("\n")

    for sentence1 in split_by_line_breaks:
        if fuzz.ratio("Degree equivalency", sentence1) > 80:
            asset_block = asset_block.replace(sentence1, "\n")

    asset_block = clean_block(asset_block)

    return asset_block


def sentence_split(requirement_block_text):
    # Regex for identifying different sentences, consider the conditions separated by the | (OR) symbol.
    requirement_list = re.split(r"^(?=\*+)(?!\s)|\n\n|\n[-.o•]\s*(?=[A-Z])|[;.]\s*\n", requirement_block_text, 0,
                                re.MULTILINE)
    return requirement_list


def create_requirement_list(requirement_block_text):
    # Such as *Recent
    requirement_list = sentence_split(requirement_block_text)
    joining_list = ["The following combinations", "select up to", "not limited to"]
    forbidden_list = ["indeterminate"]
    for idx, sentence in enumerate(requirement_list):
        for forbidden in forbidden_list:
            if forbidden in sentence.lower():
                requirement_list[idx] = ""
        for joining_string in joining_list:
            if joining_string in sentence:
                requirement_list[idx] = "".join(requirement_list[idx:])
                return requirement_list[:idx + 1]

    list(set(requirement_list))
    return requirement_list


def clean_out_definitions(requirement_block_text, definitions):
    for definition in definitions:
        requirement_block_text = requirement_block_text.replace(definition, "")
    return requirement_block_text


def extract_definitions(requirement_block_text):
    single_line_break_list = sentence_split(requirement_block_text)
    print("Sentences:" + str(single_line_break_list))
    definitions = []
    defintion_key = ["defined as", "acquired through", "acquired over", "refers to", "defined by"]
    for sentence in single_line_break_list:
        sentence = sentence.strip()
        for key in defintion_key:
            if key in sentence.lower():
                definitions.append(sentence)
                break

    for idx, item in enumerate(definitions):
        if idx + 1 != len(definitions):
            for index, item2 in enumerate(definitions[idx + 1:]):
                if fuzz.partial_ratio(item, item2) > 70:
                    definitions[index] = ""

    cleaned_definitions = []
    for definition in definitions:
        if definition != "":
            cleaned_definitions.append(definition)
    print("Definitions:" + str(cleaned_definitions))

    return cleaned_definitions


def is_definition_in_list(definition, definitions_to_append):
    if definition in definitions_to_append:
        return False

    return True


def assign_description(item, definitions):
    # Determine first word of definitions
    list_of_known_definitions = []
    for definition in definitions:
        definition = re.sub(r"[^a-zA-Z0-9]+", ' ', definition)
        definition = definition.strip()
        if definition.startswith("The"):
            definition = definition.replace("The", "").strip()
        list_of_known_definitions.append(definition.split(" ", 1)[0])
    if len(list_of_known_definitions) > 0:
        # If first word is in the statement, add definition
        definitions_to_append = ""
        for known_definition in list_of_known_definitions:
            known_definition = known_definition.lower()
            my_regex = known_definition + r"\*+|\*+" + known_definition
            if re.search(my_regex, item, re.IGNORECASE):
                for definition in definitions:
                    if known_definition in definition.lower() and is_definition_in_list(definition,
                                                                                        definitions_to_append):
                        definitions_to_append = definitions_to_append + "\n\n" + definition
        return item + definitions_to_append

    return item


def extract_headers(requirement_block_text, header_pattern):
    list_of_headers = re.findall(header_pattern, requirement_block_text, re.MULTILINE)

    return list_of_headers


def is_header_present(requirement_block_text, header_pattern):
    return re.search(header_pattern, requirement_block_text, re.MULTILINE)


def extract_sections_with_headers(requirement_block_text, list_of_headers):
    sections = []

    for index, header in enumerate(list_of_headers):

        if index + 1 != len(list_of_headers):
            section_text = text_between(list_of_headers[index], list_of_headers[index + 1], requirement_block_text)
            sections.append((header, section_text))
        else:
            section_text = requirement_block_text.rsplit(list_of_headers[index], 1)[1]
            sections.append((header, section_text))
    return sections


def extract_sections_without_headers(requirement_block_text, requirement_type, header_pattern):
    definitions = extract_definitions(requirement_block_text)
    requirement_block_text = clean_out_definitions(requirement_block_text, definitions)
    requirement_block_text = clean_out_titles(requirement_block_text, header_pattern)
    return [(requirement_type, requirement_block_text)]


def identify_sections(requirement_block_text, requirement_type):
    # Regex for identifying different types of headers, consider the conditions separated by the | (OR) symbol.
    header_pattern = r"^Stream \d:.+\n|^\s*[A-Z].+:\s*(?!.)|^\s*[A-Z ]{2,}\n|^\s*[A-Z][a-z]+\s*\n|^►.+:|" \
                     r"^[A-Z][a-z]+:\s*|^[A-Z]+\d:|^[A-Z][a-z A-Z]{0,30}(?![.;:])\n|^[A-Z]+\s*-\s*[A-Z]+\n|^[A-Z]+\d+\.(?=\s*[A-Z])"
    list_of_headers = extract_headers(requirement_block_text, header_pattern)
    if is_header_present(requirement_block_text, header_pattern):
        return extract_sections_with_headers(requirement_block_text, list_of_headers)
    else:
        return extract_sections_without_headers(requirement_block_text, requirement_type, header_pattern)


def is_definition(text):
    defintion_key = ["defined as", "acquired through", "acquired over", "refers to", "defined by"]

    for key in defintion_key:
        if key in text:
            return True

    return False


def is_pass_filter(section):
    list_of_forbidden_sections = ["Knowledge:", "Abilities and Skills:", "Personal Suitability:"]

    for forbidden in list_of_forbidden_sections:
        if fuzz.ratio(forbidden, section[0]):
            return False

    return True


def write_text_file(filename, filetext):
    text_file = open(filename + ".txt", "w")
    text_file.write(filetext)
    text_file.close()
    pass


def generate_requirements(requirement_block_text, position, requirement_type,
                          requirement_abbreviation):
    requirement_list = []
    requirement_model_list = []
    definitions = []
    x = 1
    # write_text_file(requirement_type, requirement_block_text)

    # Identify Sections
    sections = identify_sections(requirement_block_text, requirement_type)

    # For each section...
    for section in sections:

        # If it contains a definition...
        if is_definition(section[1].strip()):
            # Extract definitions
            definitions = extract_definitions(section[1])
            # Add to the list of things to be added after removing the definitions
            requirement_list = requirement_list + create_requirement_list(
                clean_out_definitions(section[1], definitions))
        # else just add it to the list of things to be added.
        elif is_pass_filter(section):
            requirement_list = requirement_list + create_requirement_list(section[1])

    for item in requirement_list:
        if item.strip() != "":
            item = scrub_extra_whitespace(item.strip())
            item.replace("\n", "")
            requirement_model_list.append(
                Requirement(position=position,
                            requirement_type=requirement_type,
                            abbreviation=requirement_abbreviation + str(x),
                            description=assign_description(item, definitions)))
            x = x + 1
    return requirement_model_list


def assign_single_line_values(position, pdf_poster_text):
    is_description_parsing = False
    is_salary_parsing = False

    # A loop that extracts single line position fields like salary or reference number. Also extracts description.
    reg_salary = re.compile(r'\d+,\d+|\$\d+.\d+ to \$\d+.\d+|salary')
    for item in pdf_poster_text.split("\n"):

        if reg_salary.search(item):
            salary = item.strip()
            is_description_parsing = False
            is_salary_parsing = True
        if is_description_parsing:
            position.description = position.description + " " + item.strip()
        if is_salary_parsing:
            position.salary = position.salary + " " + item.strip()
        if "Reference number" in item:
            position.reference_number = item.strip().split(": ")[1]
        elif "Selection process number" in item:
            position.selection_process_number = item.strip().split(": ")[1]
            is_description_parsing = True
        elif "Closing date" in item:
            position.date_closed = extract_closing_date(item)
            is_salary_parsing = False
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

    position.position_title = extract_job_title(pdf_poster_text)

    position.open_to = extract_who_can_apply(pdf_poster_text)

    position = assign_single_line_values(position, pdf_poster_text)

    list_of_requirements = extract_req_list(pdf_poster_text, position)

    position.save()

    for item in list_of_requirements:
        item.position = position
        item.save()

    dictionary = {
        'position': position
    }

    return dictionary


def download_temp_pdf(url):
    download_path = os.getcwd() + "/tempPDF.pdf"
    # Chrome settings for the Selenium chrome window.
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--whitelisted-ips")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    desired_capabilities = DesiredCapabilities.CHROME
    desired_capabilities.update(chrome_options.to_capabilities())
    driver = webdriver.Remote(command_executor='http://selenium:4444/wd/hub',
                              desired_capabilities=desired_capabilities)
    # Opens the page using the url, waits for 2 seconds so ajax commands can process.
    driver.get(url)
    delay = 2  # seconds
    time.sleep(delay)
    # Write the html to a temporary pdf file.
    HTML(string=driver.page_source).write_pdf(download_path)
    driver.close()
    return download_path


def parse_poster_text_from_url(download_path):
    # Extract the poster text read from the temporary pdf file.
    file_data = tika.parser.from_file(download_path, 'http://tika:9998/tika')
    raw_text = file_data['content']

    job_poster_text = "1. Home" + raw_text.split("1. Home", 1)[1]
    if "Share this page" in job_poster_text:
        job_poster_text = "Home" + job_poster_text.split("Share this page", 2)[2]
        job_poster_text = scrub_raw_text(job_poster_text)

    os.remove(download_path)
    return job_poster_text


def correct_poster_for_external_access(job_poster_text):
    for sentence in job_poster_text.split("\n"):
        if "Logout Applicant Number" in sentence:
            to_find = sentence
            job_poster_text = job_poster_text.replace(to_find, "Home", 1)

    return job_poster_text


def parse_poster_text_from_file(pdf_file):
    # Extract the poster text read from the temporary pdf file.
    file_data = tika.parser.from_buffer(pdf_file, 'http://tika:9998/tika')
    job_poster_text = file_data['content']
    job_poster_text = correct_poster_for_external_access(job_poster_text)
    job_poster_text = scrub_raw_text(job_poster_text)

    return job_poster_text


def parse_upload(position):
    # checking for the existence of the pdf upload. If true, convert uploaded pdf into text
    # using tika and process using find_essential_details method. If false, process url.

    if position.pdf.name:
        job_poster_text = parse_poster_text_from_file(position.pdf)
    elif position.url_ref:
        download_path = download_temp_pdf(position.url_ref)
        job_poster_text = parse_poster_text_from_url(download_path)
    else:
        return {'errors': ErrorMessages.no_pdf_or_url_submitted}

    if "Selection process number:" in job_poster_text:
        return find_essential_details(job_poster_text, position)
    else:
        return {'errors': ErrorMessages.incorrect_pdf_file}
