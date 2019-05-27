import os
import re
import tempfile

import tika
from geotext import GeoText
from tika import parser
import pdfkit
from django.db import models

from screendoor.forms import CreatePositionForm
from screendoor_app.settings import BASE_DIR
from .models import Position


def printCollectedInformation(jobTitle, closingDate, spotsLeft, salaryMin, salaryMax, classification, description, whoCanApply, referenceNumber, selectionProcessNumber, url_ref , pdf, education, experience, assets):

    print("Job Title : " + jobTitle)
    print("Closing Date : " + closingDate)
    print("Available Positions : " + spotsLeft)
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

def extractJobTitle(text):

    jobTitle = "N/A"

    if "Reference" in text:
        jobTitle = text.split('Home', 1)[1].split("Reference", 1)[0]
        jobTitle = " ".join(jobTitle.split())

    return jobTitle

def findEssentialDetails(text, path, position):

    from .models import Requirement

    referenceNumber = "N/A"
    selectionProcessNumber = "N/A"
    whoCanApply = "N/A"
    closingDate = "N/A"
    spotsLeft = "N/A"
    salary = "N/A"
    description = "N/A"
    assetBlock = "N/A"
    essentialBlock = "N/A"
    education = "N/A"
    experience = "N/A"
    salaryMin = "N/A"
    salaryMax = "N/A"

    text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^mailto?:*[\r\n]*', '', text, flags=re.MULTILINE)
    text = text.strip("\n\n")
    print("////////// "+path+" //////////\n")


    jobTitle = extractJobTitle(text)

    # Get Essentials Block
    if "(essential qualifications)" in text:
        if "If you possess any" in text:
            essentialBlock = text.split('(essential qualifications)', 1)[1].split("If you possess any", 1)[0]
        elif "The following will be applied / assessed" in text:
            essentialBlock = text.split('(essential qualifications)', 1)[1].split("The following will be applied / assessed at a later date", 1)[0]
    # Get Asset Block
    if "(other qualifications)" in text:
        assetBlock = text.split('(other qualifications)', 1)[1].split("The following will be ", 1)[0]

    # Get Education and Experience Requirements
    if "Degree equivalency\n" in essentialBlock:
        education = essentialBlock.split("Degree equivalency\n", 1)[0]
        education = education.lstrip()
        education = education.rstrip()

        experience = essentialBlock.split("Degree equivalency\n", 1)[1]
        experience = experience.lstrip()
        experience = experience.rstrip()

    elif "Experience:" in text:
        experience = text.split('Experience:', 1)[1].split("The following will be", 1)[0]

    # Get Asset Requirements

    assets = assetBlock
    assets = assets.lstrip()
    assets = assets.rstrip()

    # Extract Single line elements
    parsing = False
    for item in text.split("\n"):

        if '$' in item:
            salary = item.strip()
            salaryMin = salary.split(" to ", 1)[0]
            salaryMax = salary.split(" to ", 1)[1]
            parsing = False
        if parsing:
            description = description + " " + item.strip()
        elif "Reference number" in item:
            referenceNumber = item.strip().split(": ")[1]
        elif "Selection process number" in item:
            selectionProcessNumber = item.strip().split(": ")[1]
            parsing = True
        elif "Who can apply" in item:
            whoCanApply = item.strip().split(": ")[1]
        elif "Closing date" in item:
            closingDate = item.strip().split(": ")[1]
        elif "Positions" in item:
            spotsLeft = item.strip().split(": ")[1]

    description = description.replace('N/A  ', '', 1)
    classification = re.findall(r"([A-Z][A-Z][x-]\d\d)", description)[0]
    position.position_title = jobTitle,
    position.date_closed = closingDate,
    position.num_positions = spotsLeft,
    position.salary_min = salaryMin,
    position.salary_max = salaryMax,
    position.classification = classification,
    position.description = description,
    position.open_to = whoCanApply,
    position.reference_number = referenceNumber,
    position.selection_process_number = selectionProcessNumber

    requirementEducation = Requirement(position=position, requirement_type="educations", abbreviation="", description=education)
    requirementExperience = Requirement(position=position, requirement_type="experience", abbreviation="", description=experience)
    requirementAssets = Requirement(position=position, requirement_type="assets", abbreviation="", description=assets)



    printCollectedInformation(jobTitle, closingDate, spotsLeft, salaryMin, salaryMax, classification, description, whoCanApply, referenceNumber, selectionProcessNumber,position.url_ref,position.pdf,education,experience,assets)
    print("Hola, This means parse poster script is functional")
    return position


def doChecks(posterText):
    if "This is not a real advertisement" in posterText:
        return False
    if "We couldn't find that" in posterText:
        return False
    if "File not found" in posterText:
        return False
    if "Notification of Consideration" in posterText:
        return False
    if "Appointment of: " in posterText:
        return False
    if "Reference number:" not in posterText:
        return False
    return True


def scrapeFromGovJobs(govNum, counter):
    for x in range(0, counter):

        url = 'https://emploisfp-psjobs.cfp-psc.gc.ca/psrs-srfp/applicant/page1800?poster=' + str(govNum + x)
        filePath = 'Sample Job Posters/Sample Poster' + str(x) + '.pdf'

        try:
            pdfkit.from_url(str(url), str(filePath))
        except:
            pass

        fileData = tika.parser.from_file(filePath)
        jobPosterText = fileData['content']

        if doChecks(jobPosterText) is False:
            continue

        findEssentialDetails(jobPosterText, filePath)

        return

def parseUrlOrFile(position):


    print("THIS SHOULD PRINT FIRST")

    if position.pdf.name:
        print("THIS SHOULD PRINT SECOND")
        os.chdir("..")
        pdfFilePath = os.path.join(BASE_DIR, 'positions/Sample_Job_Poster_3.pdf')
        print(pdfFilePath)
        fileData = tika.parser.from_file(pdfFilePath,'http://tika:9998/tika')
        jobPosterText = fileData['content']
        position = findEssentialDetails(jobPosterText, pdfFilePath, position)
    else:
        url = position.url_ref
        temp = tempfile.NamedTemporaryFile()
        filePath = temp.name
        try:
            pdfkit.from_url(str(url), str(filePath))
        except:
            pass
        fileData = tika.parser.from_file(filePath)
        jobPosterText = fileData['content']
        position = findEssentialDetails(jobPosterText, filePath, position)
        os.remove('uploadedPoster_1.pdf')

    return position
