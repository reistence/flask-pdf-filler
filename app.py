import sys
import os
import re
import zipfile
from flask import Flask
from flask import render_template, redirect, request, send_file
from werkzeug.utils import secure_filename

import pdfrw
import openpyxl

app = Flask(__name__)


UPLOAD_FOLDER = './bho'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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





    

    # Create a zip folder
    zip_filename = 'files.zip'
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(os.path.join(app.config['UPLOAD_FOLDER'], excel_filename), excel_filename)
        zipf.write(os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename), pdf_filename)

    # Return the download link to the zip folder
    return render_template('generazione.html', zip_filename=zip_filename)



@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)


