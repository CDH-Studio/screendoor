# ////////////////////////////////////////START IMPORTS//////////////////////////////////
import os
import re
import time
import tika
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from weasyprint import HTML
from dateutil import parser as dateparser
from fuzzywuzzy import fuzz
from tika import parser
from .models import Requirement
from .uservisibletext import ErrorMessages

# ////////////////////////////////////////END IMPORTS////////////////////////////////////
tika.TikaClientOnly = True


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

    if education == "":
        for sentence1 in split_by_line_breaks:
            if fuzz.ratio("experience", sentence1.lower()) > 80:
                education = essential_block.split(sentence1, 1)[0]

    education = clean_block(education)

    return education


def extract_experience(essential_block):
    experience = ""
    split_by_line_breaks = essential_block.split("\n")

    for sentence1 in split_by_line_breaks:
        if fuzz.ratio("Degree equivalency", sentence1) > 80:
            experience = essential_block.split(sentence1, 1)[1]

    if experience == "":
        for sentence1 in split_by_line_breaks:
            if fuzz.ratio("experience", sentence1.lower()) > 80:
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


def extract_classification(description):
    # Regex string that looks for the qualification level in  the form of two capital letters and two numbers
    # separated by a hyphen.
    classification = ""
    if re.search(r"([A-Z][A-Z][x-]\d\d)", description):
        classifications = re.findall(r"([A-Z][A-Z][x-]\d\d)", description, re.MULTILINE)
        classification = "".join(classifications)
    return classification


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


def find_next_header(text):
    text = text.split("(essential for the job)")[1]
    split_by_line_breaks = text.split("\n")
    list_of_headers = ["The following may be", "Conditions of employment", "The following will be applied", "Other information"]

    for line in split_by_line_breaks:
        for header in list_of_headers:
            if header.lower() in line.lower():
                return header
    return None


def extract_asset(text):
    asset_block = ""

    # Some posters have an assets section found between other qualifications and the statement "The following will be"

    if "(other qualifications)" in text:
        asset_block = text_between('(other qualifications)', "The following will be ", text)
    elif "(essential for the job)" in text:
        header = find_next_header(text)
        asset_block = text_between('(essential for the job)', header, text)

    split_by_line_breaks = asset_block.split("\n")

    for sentence1 in split_by_line_breaks:
        if fuzz.ratio("Degree equivalency", sentence1) > 80:
            asset_block = asset_block.replace(sentence1, "\n")
        if "Information on language requirements" in asset_block:
            asset_block = asset_block.split("Information on language requirements")[1]
    asset_block = clean_block(asset_block)

    return asset_block


def sentence_split(requirement_block_text):
    # Regex for identifying different sentences, consider the conditions separated by the | (OR) symbol.
    requirement_list = re.split(
        r"^(?=\*+)(?!\s)|\n\n|(?<!or)\n[-.o•►→]\s*(?=[A-Z*])|(?<!e\.g)^[;.]\s*\n|^[A-Za-z]+\d+\.(?=\s*[A-Z])|^[A-Z]+\d+(?=\s*[A-Z])|^(?=Experience)|^[A-Za-z]+\d\s*:|^[A-Za-z]+\d\s*-",
        requirement_block_text, 0,
        re.MULTILINE)
    return requirement_list


def create_requirement_list(requirement_block_text, joining_list, forbidden_list):
    # Such as *Recent

    requirement_list = sentence_split(requirement_block_text)

    for idx, sentence in enumerate(requirement_list):
        for forbidden in forbidden_list:
            if forbidden in sentence.lower():
                requirement_list[idx] = ""
        for joining_string in joining_list:
            if joining_string in sentence and ":" in sentence and idx + 1 != len(requirement_list):
                offset = idx + 1
                for index2, item2 in enumerate(requirement_list[offset:], offset):
                    if item2.startswith(("•", ".")):
                        requirement_list[idx] = requirement_list[idx] + "\n" + item2
                        requirement_list[index2] = ""

    list(set(requirement_list))
    return requirement_list


def clean_out_definitions(requirement_block_text, definitions):
    for definition in definitions:
        requirement_block_text = requirement_block_text.replace(definition, "")
    return requirement_block_text


def extract_definitions(requirement_block_text, definition_key, definition_regex):
    sentences = sentence_split(requirement_block_text)
    definitions = []
    for sentence in reversed(sentences):
        sentence = sentence.strip()
        for key in definition_key:
            if key.lower() in sentence.lower():
                definitions.append(sentence)
        if re.search(definition_regex, sentence):
            definitions.append(sentence)

    cleaned_definitions = []
    for definition in definitions:
        if definition != "":
            cleaned_definitions.append(definition)
    return cleaned_definitions


def is_definition_in_list(definition, definitions_to_append):
    if definition in definitions_to_append:
        return False

    return True


def assign_description(item, definitions):
    # Determine first word of definitions
    key_phrase_list = []
    for definition in definitions:
        # Removes special symbols.
        definition = re.sub(r"[^a-zA-Z0-9]+", ' ', definition)
        definition = definition.strip()
        definition = re.sub(r"\s+", " ", definition)
        first_few_words = definition.split(" ", 3)

        if first_few_words[0].lower() == "the":
            key_phrase_list.append(first_few_words[1])
        elif first_few_words[0].isdigit():
            key_phrase_list.append(first_few_words[0])
        elif first_few_words[1][0].isupper():
            key_phrase_list.append(first_few_words[0] + " " + first_few_words[1])
        else:
            key_phrase_list.append(first_few_words[0])
    if len(key_phrase_list) > 0:
        # If key phrase is in the statement, add definition
        definitions_to_append = ""
        for key_phrase in key_phrase_list:
            key_phrase = key_phrase.lower()
            my_regex = key_phrase
            if re.search(my_regex, item, re.IGNORECASE):
                for definition in definitions:
                    if key_phrase in definition.lower() and is_definition_in_list(definition,
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
    sections = [("non-headered-text", requirement_block_text.split(list_of_headers[0], 1)[0])]
    for index, header in enumerate(list_of_headers):

        if index + 1 != len(list_of_headers):
            section_text = text_between(list_of_headers[index], list_of_headers[index + 1], requirement_block_text)
            sections.append((header, section_text))
        else:
            section_text = requirement_block_text.rsplit(list_of_headers[index], 1)[1]
            sections.append((header, section_text))
    return sections


def extract_sections_without_headers(requirement_block_text, requirement_type, header_pattern, definition_key):
    return [(requirement_type, requirement_block_text)]


def identify_sections(requirement_block_text, requirement_type, definition_key):
    # Regex for identifying different types of headers, consider the conditions separated by the | (OR) symbol.
    header_pattern = r"^[A-Za-z]+ \d:.+\n|^\s*[A-Z].{0,40}:\s*(?!.)|^\s*[A-Z][a-z]+\s*\n|^►.+:|^[A-Z][a-z]+:\s*|^[A-Za-z]+:|^(?<!.\n)[A-Z][a-z A-Z]{0,30}(?![.;:])\n|^[A-Z]+\s*-\s*.+\n|^education:|^experience:|^[A-Z]+\s*\(.+\)|^.+ - .+:"
    list_of_headers = extract_headers(requirement_block_text, header_pattern)
    if is_header_present(requirement_block_text, header_pattern):
        return extract_sections_with_headers(requirement_block_text, list_of_headers)
    else:
        return extract_sections_without_headers(requirement_block_text, requirement_type, header_pattern,
                                                definition_key)


def is_definition(text, definition_key, definition_regex):
    pattern = re.compile(definition_regex, re.MULTILINE)

    for key in definition_key:
        if key in text:
            return True
    if pattern.match(text):
        return True
    return False


def is_pass_filter(section, list_of_forbidden_sections):
    for forbidden in list_of_forbidden_sections:
        if fuzz.partial_ratio(forbidden.lower(), section[0].lower()) > 80:
            return False

    return True


def write_text_file(filename, filetext):
    text_file = open(filename + ".txt", "w")
    text_file.write(filetext)
    text_file.close()
    pass


def check_for_duplicates_and_errors(requirement_list):
    for index1, item1 in enumerate(requirement_list):
        if index1 + 1 != len(requirement_list):
            offset = index1 + 1
            for index2, item2 in enumerate(requirement_list[offset:], offset):
                if item1 == item2:
                    requirement_list[index2] = ""
        if len(item1) < 5:
            requirement_list[index1] = ""
        if item1.endswith("."):
            item1 = item1[:len(item1) - 2]
        if item1.startswith("."):
            item1 = item1[1:]
        item1 = item1.strip("►")
        item1 = item1.strip("→")
        item1 = item1.strip("*")
        item1 = item1.strip("•")
        requirement_list[index1] = item1

    return requirement_list


def generate_requirements(requirement_block_text, position, requirement_type,
                          requirement_abbreviation):
    requirement_list = []
    requirement_model_list = []
    definitions = []
    # Text before first header is labelled non-headered-text
    list_of_forbidden_sections = ["knowledge:", "abilities and skills:", "personal suitability:", "note:",
                                  "definitions:", "competencies", "Written Communication", "abilities", "Adaptability",
                                  "Leadership", "Reliability"]
    definition_key = ["defined as", "acquired through", "acquired over", "refers to", "means more than",
                      "assessed based", "completion of grade", "may include", "defined by"]
    definition_regex = r"^\**\s*.{,30}:(?=...)"
    joining_phrase_list = ["following combinations", "such as"]
    forbidden_sentence_list = ["indeterminate", "refer to the link", "follow the link", "must always have a degree",
                               "must meet all", "deciding factor", "provide appropriate", "being rejected",
                               "responsible for obtaining", "must be provided", "diversity is our strength",
                               "Attention to detail", "Effective interpersonal relationships", "when describing how",
                               "must have been obtained", "applicants must"]

    # Identify Sections
    sections = identify_sections(requirement_block_text, requirement_type, definition_key)

    # For each section...
    for section in sections:
        # If it contains a definition...
        if is_definition(section[1].strip(), definition_key, definition_regex):
            definitions = extract_definitions(section[1], definition_key, definition_regex)
        # Add it to the list of things to be added.
        if is_pass_filter(section, list_of_forbidden_sections):
            requirement_list = requirement_list + create_requirement_list(
                clean_out_definitions(section[1], definitions), joining_phrase_list, forbidden_sentence_list)
    requirement_list = check_for_duplicates_and_errors(requirement_list)

    x = 1
    for item in requirement_list:
        if item.strip() != "":
            item = scrub_extra_whitespace(item.strip())
            item.replace("\n", "")
            requirement_model_list.append(
                Requirement(position=position,
                            requirement_type=requirement_type,
                            abbreviation=requirement_abbreviation + str(x),
                            description=
                            # assign_description(item, definitions)
                            item
                            ))
            x = x + 1
    return requirement_model_list


def extract_reference_number(pdf_poster_text):
    if "Reference number:" in pdf_poster_text:
        reference_number = text_between("Reference number: ", "\n", pdf_poster_text)
        return reference_number
    return ""


def extract_selection_process_number(pdf_poster_text):
    if "Selection process number:" in pdf_poster_text:
        selection_process_number = text_between("Selection process number: ", "\n", pdf_poster_text)
        return selection_process_number
    return ""


def extract_date_closed(pdf_poster_text):
    if "Closing date:" in pdf_poster_text:
        closing_date = text_between("Closing date: ", "\n", pdf_poster_text)
        date = closing_date.rsplit(",", 1)[0]
        closing_date = dateparser.parse(date)
        return closing_date
    return ""


def extract_salary(pdf_poster_text):
    single_line_breaked_list = pdf_poster_text.split("\n")

    for line in single_line_breaked_list:
        if re.search(r"\$", line):
            salary = line
            return salary
    return ""


def extract_open_positions(pdf_poster_text):
    if "Positions to be filled:" in pdf_poster_text:
        open_positions = text_between("Positions to be filled: ", "\n", pdf_poster_text)
        return open_positions
    elif "Position:" in pdf_poster_text:
        open_positions = text_between("Position: ", "\n", pdf_poster_text)
        return open_positions
    return ""


def print_variables(position):
    print("TITLE: " + position.position_title)
    print("OPEN TO: " + position.open_to)
    print("REFERENCE NUMBER: " + position.reference_number)
    print("SELECTION PROCESS NUMBER: " + position.selection_process_number)
    print("DATE CLOSED: " + str(position.date_closed))
    print("POSITIONS: " + str(position.num_positions))
    print("SALARY: " + position.salary)
    print("DESCRIPTION: " + position.description)
    print("CLASSIFICATION: " + position.classification)

    pass


def extract_non_text_block_information(position, pdf_poster_text):
    os.chdir(os.getcwd())
    header_text = pdf_poster_text.split("Important messages")[0]
    position.position_title = extract_job_title(header_text)

    position.open_to = extract_who_can_apply(header_text)

    position.reference_number = extract_reference_number(header_text)

    position.selection_process_number = extract_selection_process_number(header_text)

    position.date_closed = extract_date_closed(header_text)

    position.num_positions = extract_open_positions(pdf_poster_text)

    position.salary = extract_salary(header_text)

    position.description = text_between(position.selection_process_number, position.salary, header_text)

    position.classification = extract_classification(position.description)

    # print_variables(position)

    return position


def scrub_raw_text(pdf_poster_text):
    os.chdir(os.getcwd())
    # Removes lines starting with https or mailto
    pdf_poster_text = re.sub(r"^\nhttp(?:(?!abc)(?!\n\n).)*\s*", '', pdf_poster_text, 50,
                             flags=re.MULTILINE | re.DOTALL)
    pdf_poster_text = pdf_poster_text.strip()
    pdf_poster_text = re.sub(r"^mailto?:*[\r\n]*", '', pdf_poster_text, 50, flags=re.MULTILINE)
    pdf_poster_text = pdf_poster_text.strip()
    pdf_poster_text = re.sub(r"^\s*\d{1,2}\/\d{1,2}\/\d{4}.+\n", "", pdf_poster_text, 50, flags=re.MULTILINE)
    pdf_poster_text = pdf_poster_text.strip()
    pdf_poster_text = re.sub(
        r"//www.+html",
        "", pdf_poster_text, 50, flags=re.MULTILINE)
    pdf_poster_text = pdf_poster_text.strip()
    pdf_poster_text = re.sub(r'\n\n+', '\n\n', pdf_poster_text)
    pdf_poster_text = pdf_poster_text.strip()
    pdf_poster_text = pdf_poster_text.replace("–", "-")

    return pdf_poster_text


def find_essential_details(pdf_poster_text, position):
    # The mother of all methods, find_essential_details uses all the other methods to parse the job poster.
    position = extract_non_text_block_information(position, pdf_poster_text)

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
    os.chdir("..")
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
    os.chdir("..")
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
