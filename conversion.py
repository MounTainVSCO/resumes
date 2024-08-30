import openai, cloudconvert, requests
from bs4 import BeautifulSoup
import pdfkit, time
import openai
import re
from bs4 import BeautifulSoup, NavigableString

api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiMjhiNTU5YmQ2MWUzOWI4MmM1YjI5Y2Q5ZTA1NTYyZWFlMjU2ZmNmMGMzNGY5NmM4MjRjN2I2ZmU2YTgzNDMzM2RjM2I1Nzk5NjEwZGQxOWIiLCJpYXQiOjE3MjQ5ODc1MjguMDA2ODE5LCJuYmYiOjE3MjQ5ODc1MjguMDA2ODIxLCJleHAiOjQ4ODA2NjExMjguMDAyMjM0LCJzdWIiOiI2OTQ0MDY0OCIsInNjb3BlcyI6WyJ1c2VyLnJlYWQiLCJ1c2VyLndyaXRlIiwidGFzay5yZWFkIiwidGFzay53cml0ZSIsIndlYmhvb2sucmVhZCIsIndlYmhvb2sud3JpdGUiLCJwcmVzZXQucmVhZCIsInByZXNldC53cml0ZSJdfQ.J852PkmJeXRLQ1DLh77oCC0MfYchjo4ENTNRD3t7Km9ZnxUk3BDcWD9vBNrb6OUR0_ev1EcmyxBgzHnyDfiwZRp2dKmw4RELeOKkkenyp_Q1Dd-obtv8qOYk8qq6J7ihkPcLTVIpvG1l7XVNKLHfCt_jd3cGTE-nNXLKmtguG2GTPxwBedZKYGtxX_TUQDsMsoa7HY8dRMM-o7eixVgj0mCSulAWuk_PiS53kniS-9vn1GscKYhRaqz3l0ZaZCzLdR2h9bObpkWu5KTjIIKzb0jbRF-fcw31vDyITbKnC02FCiRw0qunfCJj-Za280_EWHRBa2_fR5CxdKm63NnOGkjFZ_kP3ZerxxtrnaVtWJdg-mom4UHcvvejq5595MpBJEZcqXp4oWKzwWaXI2Y1xjl63VBl2lH_luVxQ7R4CWQmKMamYnDtoKliqBQHa-UcExE6ytaxV753wfdHQ7qLHurbPgT8k6gNjW7qYOEqsU1KULIxc_sEUCeJ0CM2tGG6pc4rgM9NJ7ocP8F_S80SAk3oT3EJmOJE2RhmG9PGZ9uTOB3gM1mKfeB59ykvFxyuNpuh7BjehorKzReef_Z0wglXzrcVfy8bMG-DLH3wf8Xfbi9MRE3jWDeTCIDnzw9Njv26ZUbQg48yiwtFcv2J46a5BBtCmbV0uaKYtcoN2zI'

if __name__ == '__main__':
    start = "pdf"
    target = "html"
    input_file = "Basic_Resume.docx.pdf"
    output_file = "output.html"

    cloudconvert.configure(api_key=api_key)
    job = cloudconvert.Job.create(payload={
        "tasks": {
            'import-my-file': {
                'operation': 'import/upload'
            },
            'convert-my-file': {
                'operation': 'convert',
                'input': 'import-my-file',
                'output_format': f'{target}'
            },
            'export-my-file': {
                'operation': 'export/url',
                'input': 'convert-my-file'
            }
        }
    })

    # Upload the PDF file
    upload_task_id = job['tasks'][0]['id']
    upload_task = cloudconvert.Task.find(id=upload_task_id)
    cloudconvert.Task.upload(file_name=input_file, task=upload_task)

    # Wait for the job to complete and retrieve the output URL
    job = cloudconvert.Job.wait(id=job['id'])
    export_task_id = [task['id'] for task in job['tasks'] if task['operation'] == 'export/url'][0]
    export_task = cloudconvert.Task.find(id=export_task_id)
    file = export_task['result']['files'][0]
    cloudconvert.download(filename=output_file, url=file['url'])
