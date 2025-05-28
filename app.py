from flask import Flask, request, send_file, render_template
from pdf2docx import Converter as PdfToDocxConverter
from docx2pdf import convert as DocxToPdfConverter
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import zipfile
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route('/')
def upload_form():
    return render_template('index.html')

@app.route('/routes')
def show_routes():
    return str(app.url_map)

@app.route('/convert/pdf-to-word', methods=['GET', 'POST'])
def convert_pdf_to_word():
    if request.method == 'GET':
        return "PDF to Word route is working!"
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(pdf_path)
        docx_path = os.path.join(CONVERTED_FOLDER, file.filename.rsplit('.', 1)[0] + ".docx")
        
        cv = PdfToDocxConverter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        
        return send_file(docx_path, as_attachment=True)

@app.route('/convert/word-to-pdf', methods=['GET', 'POST'])
def convert_word_to_pdf():
    if request.method == 'GET':
        return "Word to PDF route is working!"
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if not file.filename.lower().endswith('.docx'):
        return "Μόνο .docx αρχεία υποστηρίζονται για μετατροπή σε PDF."

    docx_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(docx_path)
    pdf_path = os.path.join(CONVERTED_FOLDER, file.filename.rsplit('.', 1)[0] + ".pdf")

    try:
        DocxToPdfConverter(docx_path, pdf_path)
    except Exception as e:
        return f"Σφάλμα κατά τη μετατροπή: {e}"

    return send_file(pdf_path, as_attachment=True)

@app.route('/split/pdf', methods=['GET', 'POST'])
def split_pdf():
    if request.method == 'GET':
        return "Split PDF route is working!"
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    reader = PdfReader(pdf_path)
    base_name = os.path.splitext(file.filename)[0]
    zip_path = os.path.join(CONVERTED_FOLDER, f"{base_name}_pages.zip")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            output_filename = os.path.join(CONVERTED_FOLDER, f"{base_name}_page_{i+1}.pdf")
            with open(output_filename, 'wb') as f_out:
                writer.write(f_out)
            zipf.write(output_filename, arcname=os.path.basename(output_filename))
            os.remove(output_filename)

    return send_file(zip_path, as_attachment=True)

@app.route('/convert/image-to-pdf', methods=['GET', 'POST'])
def convert_image_to_pdf():
    if request.method == 'GET':
        return "Image to PDF route is working!"
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    allowed_extensions = ['.jpg', '.jpeg', '.png']
    ext = os.path.splitext(file.filename.lower())[1]
    if ext not in allowed_extensions:
        return "Μόνο εικόνες JPG, JPEG ή PNG υποστηρίζονται."

    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)
    pdf_filename = os.path.splitext(file.filename)[0] + ".pdf"
    pdf_path = os.path.join(CONVERTED_FOLDER, pdf_filename)

    try:
        img = Image.open(image_path)
        rgb_img = img.convert('RGB')
        rgb_img.save(pdf_path)
    except Exception as e:
        return f"Σφάλμα κατά τη μετατροπή: {e}"

    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True, port=5000)
