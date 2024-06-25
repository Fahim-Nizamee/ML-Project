from flask import Flask, render_template, request, jsonify, redirect, url_for
import re
from collections import Counter
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  
    text = re.sub(r'[^a-zA-Z\s]', '', text)  
    return text

def generate_summary(text, summary_ratio=0.3):
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    stop_words = set(stopwords.words('english'))
    tokens = [word.lower() for word in words if word.lower() not in stop_words and word.isalnum()]

    word_freq = Counter(tokens)
    max_freq = max(word_freq.values())
    word_freq = {word: freq / max_freq for word, freq in word_freq.items()}

    sentence_scores = {}
    for sent in sentences:
        for word in word_tokenize(sent.lower()):
            if word in word_freq:
                if sent not in sentence_scores:
                    sentence_scores[sent] = word_freq[word]
                else:
                    sentence_scores[sent] += word_freq[word]

    summary_length = int(len(sentences) * summary_ratio)
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:summary_length]
    summary = ' '.join(top_sentences)
    return summary


def extract_keywords(text):
    words = word_tokenize(clean_text(text))
    stop_words = set(stopwords.words('english'))
    keywords = [word for word in words if word.lower() not in stop_words]
    keyword_freq = Counter(keywords)
    return keyword_freq.most_common(10)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summary', methods=['POST'])
def summary():
    text = request.form['text']
    summary_ratio = float(request.form.get('summary_ratio', 0.3))
    summary = generate_summary(text, summary_ratio)
    keywords = extract_keywords(text)

    return jsonify({
        'summary': summary,
        'keywords': keywords
    })

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/sum')
def sum():
    return render_template('summary.html')

if __name__ == '__main__':
    app.run(debug=True)
