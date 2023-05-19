from flask import Flask
from flask import render_template, redirect, request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/gen", methods=['POST'])
def generate():
    excel_file = request.files['excelFile']
    pdf_file = request.files['pdfFile']
    field_nr = int(request.form['fieldNr'])
    campo_values = [request.form.get(f'campo-{i}') for i in range(field_nr)]
    print(excel_file, pdf_file)
    if campo_values:
        print(campo_values)
    # return render_template('generazione.html')
    return'Form submitted successfully'
