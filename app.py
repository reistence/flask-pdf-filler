import sys
import os
import re
import shutil
import zipfile
from flask import Flask
from flask import render_template, redirect, request, send_file
from werkzeug.utils import secure_filename

import pdfrw
import openpyxl

app = Flask(__name__)


UPLOAD_FOLDER = './upload'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

OUTPUT_FOLDER = './output'


app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def clean_file_name(file_name):
    # remove spaces 
    file_name = file_name.replace(' ', '-')
    # Removes special characters.
    file_name = re.sub('[^A-Za-z0-9\-_]', '', file_name)
    # Replaces multiple hyphens with a single one.
    file_name = re.sub('-+', '-', file_name)
    clean_file_name = f"{file_name}"
    return clean_file_name


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/gen", methods=['POST'])
def generate():
    excel_file = request.files['excelFile']
    pdf_file = request.files['pdfFile']
    field_nr = int(request.form['fieldNr'])
    campo_values = [request.form.get(f'campo-{i}') for i in range(field_nr)]
    
    excel_filename = secure_filename(excel_file.filename)  # Use the same name as the original file
    pdf_filename = secure_filename(pdf_file.filename)  # Use the same name as the original file
    excel_file.save(os.path.join(app.config['UPLOAD_FOLDER'], excel_filename))
    pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename))


    shutil.rmtree(app.config['OUTPUT_FOLDER'])
    if not os.path.exists(OUTPUT_FOLDER):
         os.makedirs(OUTPUT_FOLDER)

     # Create a zip folder
    zip_filename = excel_filename + pdf_filename +'_PDFs'
    # zip_path = os.path.join(app.config['zip_filename'],)

    template_pdf = pdfrw.PdfReader('./upload/'+pdf_filename);
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))

    workbook = openpyxl.load_workbook('./upload/'+excel_filename)
    worksheet = workbook.active
    data = []

    # Read the data from the Excel file
    for row in worksheet.iter_rows(values_only=True):
        data.append(row)

    # Iterate over the data
    for i, row in enumerate(data):
        if i == 0:  # Skip the first row
            continue
        nameToBeSaved = row[0]+'_'+row[1]
         # Create a new PDF object by copying the template
        output_pdf = pdfrw.PdfWriter()
        output_pdf.addpages(template_pdf.pages[:])

         # Fill the form fields with the data
        for page in template_pdf.pages:
            annotations = page['/Annots']
            if annotations is None:
                continue
            for annotation in annotations:
                
                if annotation['/Subtype'] == '/Widget' and '/T' in annotation:
                    field_name = annotation['/T'][1:-1]  # Remove parentheses
                
                    for name, value in zip(campo_values, row):
                        if field_name == 'number':
                            annotation.update(pdfrw.PdfDict(V=str(i), Ff=1))
                        elif field_name == name:
                            annotation.update(pdfrw.PdfDict(V=value, Ff=1))


        output_name = './output/' +pdf_filename + '_{}.pdf'.format(clean_file_name(nameToBeSaved))

        #save pdf
        output_pdf.write(output_name, template_pdf)
        # with zipfile.ZipFile(zip_path, 'w') as zipf:
        #     zipf.write( output_name, os.path.basename(output_name))
        #     # zipf.write(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename), pdf_filename)
        # with zipfile.ZipFile(zip_path, 'w') as zipf:
        #     for i, row in enumerate(data[1:], 1):  # Start from index 1 to skip the header row
        #         nameToBeSaved = row[0] + '_' + row[1]
        #         output_name = './output/' + pdf_filename + '_{}.pdf'.format(clean_file_name(nameToBeSaved))
        #         output_pdf.write(output_name, template_pdf)
        #         zipf.write(output_name, os.path.basename(output_name))



    shutil.make_archive( zip_filename, 'zip', OUTPUT_FOLDER)

    

    

    # Return the download link to the zip folder
    # return render_template('generazione.html', zip_filename=zip_filename)
    return send_file(os.path.basename(zip_filename + '.zip'), as_attachment=True)



# @app.route('/download/<filename>')
# def download_file(filename):
#     file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
#     return send_file(file_path, as_attachment=True)


