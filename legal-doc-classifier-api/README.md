# Legal Document Classifier API

This project is a Flask-based API for classifying legal documents such as contracts, court filings, and M&A agreements. The API accepts PDF file uploads and returns a JSON response with the classification results.

## Project Structure

```
legal-doc-classifier-api
├── app
│   ├── __init__.py
│   ├── api.py
│   ├── classifier.py
│   ├── pdf_utils.py
│   └── models
│       └── __init__.py
├── requirements.txt
├── README.md
└── run.py
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd legal-doc-classifier-api
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application:**
   ```
   python run.py
   ```

2. **API Endpoint:**
   - **POST /classify**
     - Upload a PDF file to classify the document.
     - Example request:
       ```
       curl -X POST -F "file=@path_to_your_file.pdf" http://localhost:5000/classify
       ```
     - Example response:
       ```json
       {
         "classification": "contract"
       }
       ```

## Dependencies

- Flask
- PyPDF2 (or similar for PDF handling)
- Any machine learning libraries used for classification

## License

This project is licensed under the MIT License - see the LICENSE file for details.