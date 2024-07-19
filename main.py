import fitz  # PyMuPDF
import os
import tempfile
from PIL import Image
from io import BytesIO
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

def get_downloads_folder():
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:  # macOS and Linux
        return os.path.join(os.path.expanduser('~'), 'Downloads')

def save_images_from_pdf(pdf_path, output_folder):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Loop through each page
    for page_number in range(len(pdf_document)):
        # Create a folder for each page
        page_folder = os.path.join(output_folder, f"page_{page_number + 1}")
        if not os.path.exists(page_folder):
            os.makedirs(page_folder)
        
        # Get the page
        page = pdf_document.load_page(page_number)
        image_list = page.get_images(full=True)
        
        # Loop through each image
        for img_index, img in enumerate(image_list, start=1):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Convert image bytes to PIL Image and save as JPEG
            image = Image.open(BytesIO(image_bytes))
            image_path = os.path.join(page_folder, f"image_{img_index}.jpeg")
            image.save(image_path, "JPEG")
            
            print(f"Saved {image_path}")

@app.route('/')
def index():
    file_name = request.args.get('file_name')
    return render_template('index.html', file_name=file_name)

@app.route('/upload', methods=['POST'])
@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return jsonify(success=False, error="No file part"), 400
    
    file = request.files['pdf']
    
    if file.filename == '':
        return jsonify(success=False, error="No selected file"), 400
    
    if file:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            # Write the uploaded file to the temporary file
            temp_pdf.write(file.read())
            temp_pdf_path = temp_pdf.name
        
        # Get the base name of the PDF file (e.g., "PS25.pdf")
        pdf_base_name = os.path.basename(file.filename)

        # Remove the file extension (e.g., "PS25")
        pdf_name_without_extension = os.path.splitext(pdf_base_name)[0]

        # Get the Downloads folder path
        downloads_folder = get_downloads_folder()

        # Output folder to save the images, now using the modified name in the Downloads folder
        output_folder = os.path.join(downloads_folder, f"Extractor_{pdf_name_without_extension}")

        try:
            save_images_from_pdf(temp_pdf_path, output_folder)
        finally:
            # Ensure the temporary file is deleted
            os.remove(temp_pdf_path)

        return jsonify(success=True, file_name=pdf_name_without_extension), 200

    return jsonify(success=False, error="Unexpected error"), 500

if __name__ == '__main__':
    app.run(debug=True)
