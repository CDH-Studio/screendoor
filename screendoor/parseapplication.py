import os


from screendoor_app.settings import BASE_DIR
from tika import parser


def find_essential_details(applicant_text, applicant):

    print(applicant_text)

    pass


def parse_application(applicant):

    os.chdir("..")
    pdf_file_path = os.path.join(BASE_DIR, applicant.pdf.url)
    file_data = parser.from_file(pdf_file_path, 'http://tika:9998/tika')
    job_poster_text = file_data['content']
    find_essential_details(job_poster_text, applicant)
    pass

