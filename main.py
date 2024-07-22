import fitz  # PyMuPDF
import os
import tempfile
from PIL import Image
from io import BytesIO
from flask import Flask, request, render_template, jsonify, send_from_directory, redirect, flash
import zipfile
import shutil

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessario per utilizzare flash

def create_zip_of_images(output_folder, zip_path):
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for foldername, subfolders, filenames in os.walk(output_folder):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zip_file.write(file_path, os.path.relpath(file_path, output_folder))

# Create the output folder if it doesn't exist
def get_output_folder():
    return os.path.join(os.path.dirname(__file__), 'output_images')

# Delete the output folder and its contents once process is done
def delete_output_folder(output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)

def save_images_from_pdf(pdf_path, output_folder):
    pdf_document = fitz.open(pdf_path)

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for page_number in range(len(pdf_document)):
        page_folder = os.path.join(output_folder, f"page_{page_number + 1}")
        if not os.path.exists(page_folder):
            os.makedirs(page_folder)

        page = pdf_document.load_page(page_number)
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image = Image.open(BytesIO(image_bytes))
            image_path = os.path.join(page_folder, f"image_{img_index}.jpeg")
            image.save(image_path, "JPEG")
            print(f"Saved {image_path}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return jsonify(success=False, error="No file part"), 400

    file = request.files['pdf']

    if file.filename == '':
        return jsonify(success=False, error="No selected file"), 400

    if file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(file.read())
            temp_pdf_path = temp_pdf.name

        output_folder = get_output_folder()
        pdf_base_name = os.path.basename(file.filename)
        pdf_name_without_extension = os.path.splitext(pdf_base_name)[0]
        
        # Creates the ZIP file name
        zip_filename = f"Extractor_{pdf_name_without_extension}.zip"
        zip_path = os.path.join(output_folder, zip_filename)

        try:
            save_images_from_pdf(temp_pdf_path, output_folder)
            create_zip_of_images(output_folder, zip_path)
            return jsonify(success=True, filename=zip_filename), 200
        finally:
            os.remove(temp_pdf_path)

    return jsonify(success=False, error="Unexpected error"), 500

@app.route('/download/<filename>')
def download_file(filename):
    output_folder = get_output_folder()
    return send_from_directory(output_folder, filename, as_attachment=True)

@app.route('/delete_folder', methods=['POST'])
def delete_folder():
    output_folder = get_output_folder()
    delete_output_folder(output_folder)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
