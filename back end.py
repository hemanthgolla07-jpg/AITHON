from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import nltk
from nltk.tokenize import sent_tokenize

# Download tokenizer data if not already present
nltk.download('punkt')

app = Flask(__name__)

# Setup SQLite DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///study.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Create uploads folder (not mandatory here, but good practice)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Models
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    # Only accept text files for now
    if not file.filename.endswith('.txt'):
        return jsonify({'error': 'Only .txt files supported'}), 400

    content = file.read().decode('utf-8')
    filename = file.filename

    doc = Document(filename=filename, content=content)
    db.session.add(doc)
    db.session.commit()

    return jsonify({'message': 'File uploaded successfully', 'doc_id': doc.id})

@app.route('/generate_quiz/<int:doc_id>', methods=['GET'])
def generate_quiz(doc_id):
    doc = Document.query.get(doc_id)
    if not doc:
        return jsonify({'error': 'Document not found'}), 404

    sentences = sent_tokenize(doc.content)
    quiz = []

    # Generate up to 5 quiz questions from first sentences (mock questions)
    for i, sent in enumerate(sentences[:5]):
        quiz.append({
            'question': f"What is the main idea of this sentence? \"{sent[:60]}...\"",
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'correct': 0  # Mock correct answer is always option 0
        })

    return jsonify({'quiz': quiz})

@app.route('/submit_quiz', methods=['POST'])
def submit_quiz():
    data = request
