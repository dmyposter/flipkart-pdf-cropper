from flask import Flask, request, send_file
import fitz  # PyMuPDF
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return '''
    <html>
    <head>
    <title>Flipkart Label & Invoice Cropper | CreativKart</title>
    <style>
        body { font-family: Arial; background: #f2f2f2; text-align: center; padding: 50px 20px; }
        form { background: white; display: inline-block; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        input[type=file] { padding: 10px; }
        input[type=submit] { padding: 10px 20px; background: #5a67d8; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
    </head>
    <body>
        <h2>Upload Flipkart PDF to Crop Label + Invoice</h2>
        <form method="post" action="/process" enctype="multipart/form-data">
            <input type="file" name="pdf" accept=".pdf"><br><br>
            <input type="submit" value="Upload and Process">
        </form>
    </body>
    </html>
    '''

@app.route('/process', methods=['POST'])
def process_pdf():
    file = request.files['pdf']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    doc = fitz.open(filepath)
    combined = fitz.open()

    for i in range(len(doc)):
        page = doc[i]

        # Label dimensions (in points)
        rect_label = fitz.Rect(183.6, 20.88, 408.96, 386.64)
        combined.new_page(width=225.36, height=365.76)
        combined[-1].show_pdf_page(fitz.Rect(0, 0, 225.36, 365.76), doc, i, clip=rect_label)

        # Invoice dimensions (in points)
        rect_inv = fitz.Rect(24.48, 383.76, 555.84, 740.88)
        combined.new_page(width=531.36, height=357.12)
        combined[-1].show_pdf_page(fitz.Rect(0, 0, 531.36, 357.12), doc, i, clip=rect_inv)

    out_path = os.path.join(OUTPUT_FOLDER, "cropped_combined.pdf")
    combined.save(out_path)
    return send_file(out_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
