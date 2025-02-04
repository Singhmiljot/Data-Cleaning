# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import os
import PyPDF2  # Add this import for PDF handling

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xlsx', 'pdf'}  # Add 'pdf' here

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Home page with file upload form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if the file is valid
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save the uploaded file
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Redirect to the cleaning page
            return redirect(url_for('clean_data', filename=file.filename))
    
    return render_template('index.html')

# Data cleaning and transformation page
@app.route('/clean/<filename>')
def clean_data(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Load the dataset
    if filename.endswith('.csv'):
        df = pd.read_csv(filepath)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(filepath)
    elif filename.endswith('.pdf'):
        # Read PDF file
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
        # Convert text to DataFrame (you may need to adjust this based on your PDF structure)
        df = pd.DataFrame([x.split() for x in text.split('\n') if x])  # Example conversion
    
    else:
        return "Unsupported file format."
    
    # Save the original dataset for display
    original_df = df.copy()
    
    # Perform data cleaning and transformation
    df = df.drop_duplicates()
    df = df.dropna()
    df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)
    
    # Save the cleaned dataset
    cleaned_filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'cleaned_' + filename)
    if filename.endswith('.csv'):
        df.to_csv(cleaned_filepath, index=False)
    elif filename.endswith('.xlsx'):
        df.to_excel(cleaned_filepath, index=False)
    elif filename.endswith('.pdf'):
        # Save cleaned PDF logic if needed
        pass
    
    # Render the results page
    return render_template('clean.html', original=original_df.to_html(), cleaned=df.to_html())

# Run the app
if __name__ == '__main__':
    app.run(debug=True)