import os
import mimetypes
import google.generativeai as genai
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 10MB limit
app.secret_key = "supersecretkey"

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Google Generative AI
GOOGLE_API_KEY = "API_Key"
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Detect file type
    mime_type, _ = mimetypes.guess_type(file.filename)
    
    if mime_type and mime_type.startswith("text"):
        try:
            with open(file_path, 'r', encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            content = "Unable to decode file as UTF-8 text."
    else:
        content = f"This file appears to be binary (e.g., {mime_type or 'unknown type'}), and cannot be displayed."

    return render_template('display.html', filename=file.filename, content=content)

@app.route('/summarize/<filename>')
def summarize(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Read the file content
    try:
        with open(file_path, 'r', encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        flash("Cannot summarize this file as it is not a readable text format.")
        return redirect(url_for('index'))

    # Use Gemini-Pro to generate a summary
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(f"Summarize this document: {content}")

    summary = response.text if response and hasattr(response, 'text') else "Failed to generate summary."

    return render_template('summary.html', filename=filename, summary=summary)

if __name__ == '__main__':
    app.run(debug=True)
