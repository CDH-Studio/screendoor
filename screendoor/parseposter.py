import os
import re
import tika
from geotext import GeoText
from tika import parser
import pdfkit
from django.db import models
from .models import Position

def printCollectedInformation(referenceNumber,selectionProcessNumber, whoCanApply, jobTitle, closingDate, spotsLeft, salary, description, education, experience, assets):
    print("Reference Number : " + referenceNumber)
    print("Selection Process Number : " + selectionProcessNumber)
    print("Who Can Apply : " + whoCanApply)
    print("Job Title : " + jobTitle)
    print("Closing Date : " + closingDate)
    print("Available Positions : " + spotsLeft)
    print("Salary Range : " + salary)
    print("Description : " + description + "\n")
    print("/////////////////  Education  ///////////////// \n" + education + "\n")
    print("/////////////////  Experience  ///////////////// \n" + experience + "\n")
    print("/////////////////  Assets  ///////////////// \n" + assets + "\n")

    return


def findEssentialDetails(text, path, position):
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
    assets = "N/A"
    jobTitle = "N/A"
    salaryMin = "N/A"
    salaryMax = "N/A"

    text = re.sub(r'^https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^mailto?:*[\r\n]*', '', text, flags=re.MULTILINE)

    text = text.strip("\n\n")
    print("////////// "+path+" //////////\n")


    # Extract Job Title
    if "Reference" in text:
        jobTitle = text.split('Home', 1)[1].split("Reference", 1)[0]
        jobTitle = " ".join(jobTitle.split())

    # Get Essentials Block
    if "(essential qualifications)" in text:
        if "If you possess any" in text:
            essentialBlock = text.split('(essential qualifications)', 1)[1].split("If you possess any", 1)[0]
        elif "The following will be applied / assessed at a later date" in text:
            essentialBlock = text.split('(essential qualifications)', 1)[1].split("The following will be applied / assessed at a later date", 1)[0]
    # Get Asset Block
    if "(other qualifications)" in text:
        assetBlock = text.split('(other qualifications)', 1)[1].split("The following will be ", 1)[0]
    elif "(may be\nneeded for the job)" in text:
        if "Conditions of employment" in text:
            assetBlock = text.split('(may be\nneeded for the job)', 1)[1].split("Conditions of employment", 1)[0]
        elif "Other information" in text:
            assetBlock = text.split('(may be\nneeded for the job)', 1)[1].split("Other information", 1)[0]


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
    city = GeoText(description).cities[0]
    department = description.split(city)[0]
    location = description.split(department)[1].split(classification)[0]

    position.position_title = jobTitle
    position.date_closed = closingDate
    position.num_positions = spotsLeft
    position.salary_min = salaryMin
    position.salary_max = salaryMax
    position.classification = classification
    position.department = department
    position.location = location
    position.open_to = whoCanApply
    position.reference_number = referenceNumber
    position.selection_process_number = selectionProcessNumber


    # printCollectedInformation(referenceNumber, selectionProcessNumber, whoCanApply, jobTitle, closingDate, spotsLeft, salary, description, education, experience, assets)

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

    if position.url_ref is None:
        pdfFilePath = position.pdf.url()
        fileData = tika.parser.from_file(pdfFilePath)
        jobPosterText = fileData['content']
        position = findEssentialDetails(jobPosterText, pdfFilePath, position)
    elif position.pdf is None:
        url = position.url_ref
        filePath = 'uploadedPoster_1.pdf'
        try:
            pdfkit.from_url(str(url), str(filePath))
        except:
            pass
        fileData = tika.parser.from_file(filePath)
        jobPosterText = fileData['content']
        position = findEssentialDetails(jobPosterText, filePath, position)
        os.remove('uploadedPoster_1.pdf')

    return position
