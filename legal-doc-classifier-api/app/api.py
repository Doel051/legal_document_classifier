from flask import Flask, request, render_template_string, send_file
from classifier import classify_document
from pdf_utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    extract_text_from_txt
)
import zipfile
import tempfile
import os
from io import BytesIO

app = Flask(__name__)

classification_result = {}

@app.route('/', methods=['GET'])
def home():
    html_form = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Legal Document Classifier</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(to right, #dbefff, #b0d4f1);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                background: #ffffff;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
                text-align: center;
                max-width: 500px;
                width: 90%;
            }
            h1 {
                color: #0a3d62;
                margin-bottom: 20px;
            }
            p {
                color: #34495e;
                font-size: 16px;
                margin-bottom: 20px;
            }
            input[type="file"] {
                padding: 10px;
                border: 2px solid #74b9ff;
                border-radius: 8px;
                background: #ecf5ff;
                font-size: 14px;
                cursor: pointer;
            }
            input[type="submit"] {
                background-color: #0984e3;
                color: white;
                border: none;
                padding: 12px 25px;
                margin-top: 20px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s ease;
            }
            input[type="submit"]:hover {
                background-color: #0652dd;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Legal Document Classifier</h1>
            <p>Select a single file (.pdf, .docx, .txt) or a .zip archive</p>
            <form action="/classify" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept=".pdf,.docx,.txt,.zip" required>
                <br>
                <input type="submit" value="Upload & Classify">
            </form>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html_form)


@app.route('/classify', methods=['POST'])
def classify():
    if 'file' not in request.files:
        return "No file uploaded.", 400

    file = request.files['file']
    filename = file.filename.lower()

    results = []

    try:
        if filename.endswith('.zip'):
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, 'uploaded.zip')
                file.save(zip_path)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                for root, _, files in os.walk(temp_dir):
                    for f in files:
                        # Skip __MACOSX and dot-underscore files
                        if "__MACOSX" in root or f.startswith("._"):
                            continue
                        full_path = os.path.join(root, f)
                        rel_path = os.path.relpath(full_path, temp_dir)
                        try:
                            if f.lower().endswith('.pdf'):
                                with open(full_path, 'rb') as doc:
                                    text = extract_text_from_pdf(doc)
                            elif f.lower().endswith('.docx'):
                                with open(full_path, 'rb') as doc:
                                    text = extract_text_from_docx(doc)
                            elif f.lower().endswith('.txt'):
                                with open(full_path, 'rb') as doc:
                                    text = extract_text_from_txt(doc)
                            else:
                                continue

                            category = classify_document(text)
                            results.append((rel_path, category))
                        except Exception as e:
                            results.append((rel_path, f"Error: {str(e)}"))
        else:
            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(file)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(file)
            elif filename.endswith('.txt'):
                text = extract_text_from_txt(file)
            else:
                return "Unsupported file type. Upload PDF, DOCX, TXT or ZIP.", 400

            category = classify_document(text)
            results.append((filename, category))

        classification_result['results'] = results

        # Build table
        rows = ""
        for file, category in results:
            if category in ['contract', 'court_filing', 'm&a_agreement']:
                display = category.upper()
            elif category.startswith("Error:"):
                display = f"<span style='color: red;'>{category}</span>"
            else:
                display = "<i>Not a legal document</i>"
            rows += f"<tr><td>{file}</td><td>{display}</td></tr>"

        result_page = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Classification Results</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #ecf5ff;
                    padding: 40px;
                }}
                h2 {{
                    color: #0a3d62;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                table {{
                    margin: 0 auto;
                    border-collapse: collapse;
                    width: 80%;
                    background: #ffffff;
                }}
                th, td {{
                    padding: 12px 20px;
                    border: 1px solid #ccc;
                    text-align: left;
                }}
                th {{
                    background-color: #74b9ff;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                .button {{
                    display: block;
                    width: 250px;
                    margin: 30px auto;
                    padding: 12px 20px;
                    text-align: center;
                    background-color: #0984e3;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                }}
                .button:hover {{
                    background-color: #0652dd;
                }}
            </style>
        </head>
        <body>
            <h2>Classification Results</h2>
            <table>
                <tr><th>File</th><th>Classification</th></tr>
                {rows}
            </table>
            <a href="/download_report" class="button">Download Report</a>
            <a href="/" class="button">Classify Another Document</a>
        </body>
        </html>
        '''
        return result_page

    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/download_report', methods=['GET'])
def download_report():
    if 'results' not in classification_result:
        return "No report found. Please classify a file first.", 400

    buffer = BytesIO()
    content = "Legal Document Classification Report\n\n"
    for file, category in classification_result['results']:
        if category.startswith("Error:"):
            display = category
        elif category in ['contract', 'court_filing', 'm&a_agreement']:
            display = category
        else:
            display = "Not a legal document"
        content += f"{file} : {display}\n"

    buffer.write(content.encode('utf-8'))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="classification_report.txt", mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
