from flask import Flask,flash, request, redirect, url_for, render_template
import requests
from bs4 import BeautifulSoup
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import string
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Uploader Page
app.secret_key = "secretkey"
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            flash('Tidak ada file yang dipilih')
            return redirect(request.url)
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('File ' + filename + ' berhasil di-upload')
        return redirect('/upload')
    
# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# create stopword remover
factory2 = StopWordRemoverFactory()
stopword = factory2.create_stop_word_remover()

# Instantiate a TfidfVectorizer object
vectorizer = CountVectorizer()

def getdata(urls,short_desc,title, articles):
    for i in range(1,3):
        # Make a request to the website
        link = 'https://www.alodokter.com/page/'+str(i)
        web = requests.get(link)

        # Create an object to parse the HTML format
        soup = BeautifulSoup(web.content,'html.parser')

        # Retrieve links
        for j in soup.findAll("card-post-index"):
            urls.append("https://www.alodokter.com"+ j.attrs['url-path'])
            short_desc.append(j.attrs['short-description'])
            title.append(j.attrs['title'])
            # img.append(j.attrs['image-url'])

    idx=0
    # For each link, we retrieve paragraphs from it, combine each paragraph as one string, and save it to articles array
    for i in urls:
        r = requests.get(i)
        soupr = BeautifulSoup(r.text,'html.parser')

        contentperarticle=[]
        for i in soupr.findAll(["p","h3","h4","li"]):
            contentperarticle.append(i.text.strip())

        articles.append(title[idx]+' '+ ' '.join(contentperarticle))
        idx+=1
 

def CountWordsArticles(df):
    # Number of column in df
    banyakkolom = len(df.columns)

    # Count number of words in each articles
    banyakkata=[0 for i in range(banyakkolom)]

    for k in range (0,banyakkolom):
        doc = df.loc[:,k].values
        count = 0
        for j in range (len(doc)):
            count = count + int(doc[j])
        banyakkata[k] = count
    return banyakkata

def clean_text(text):
    # Remove stopwords and stemming text
    text = stemmer.stem(stopword.remove(text))
    # Remove puntuation from text
    text = text.translate(str.maketrans('','',string.punctuation))
    return text

def clean_articles(articles):
    cleaned=[]
    for article in articles:
        cleaned.append(clean_text(article))
    return cleaned

def vectorize(articles):
    # It fits the data and transform it as a vector
    X = vectorizer.fit_transform(articles)    
    # Convert the X as transposed matrix
    X = X.T.toarray()
    # Create a DataFrame and set the vocabulary as the index
    df = pd.DataFrame(X, index=vectorizer.get_feature_names())
    return df

def nilaidot(vec,q_vec):
    sum = 0
    for i in range (0,len(q_vec)):
        sum = sum + vec[i]*q_vec[i]
    return sum

def panjangvektor(vector):
    sum = 0
    for i in range (0,len(vector)):
        sum = sum + (vector[i]**2)
    return (sum)**(1/2)

def get_sorted_sim(q, df):
  # Convert the query become a vector
  q = [q]
  q_vec = vectorizer.transform(q).toarray().reshape(df.shape[0],)
  
  sim = {}
  # Calculate the similarity
  for i in range(len(articles)):
      vec = df.loc[:, i].values
      if panjangvektor(vec)*panjangvektor(q_vec) != 0:
        sim[i] = nilaidot(vec,q_vec)/(panjangvektor(vec)*panjangvektor(q_vec))
      else:
          sim[i] = 0
  
  # Sort the values 
  sim_sorted = sorted(sim.items(), key=lambda x: x[1], reverse=True)
  return sim_sorted
    

# MAIN PROGRAM

# Make array containing all of articles content
articles=[]
# Array containing url of each article
urls=[]
# Array containing short description of each article
short_desc=[]
# Array containing the title of articles
title=[]
# Array containing link image
# img = []

# Get urls, short description, title, and articles data
getdata(urls,short_desc,title,articles)

# Clean articles data
articles = clean_articles(articles)
df = vectorize(articles)
banyakkolom = len(df.columns)

# Count number of words in each articles
banyakkata = CountWordsArticles(df)

@app.route('/', methods=['GET','POST'])
def index():
    q1=''
    sim_sorted=[]
    tabterm=pd.DataFrame(data=None, index=None, columns=None)
    if request.method=='POST':
        q1 = request.form['text']
        # Clean query
        q1 = clean_text(q1)
        sim_sorted = get_sorted_sim(q1, df)
        # Showing table of term
        q=[q1]
        q_vec = vectorizer.transform(q).toarray().reshape(df.shape[0],)
        tabterm = pd.DataFrame(q_vec, index=vectorizer.get_feature_names(), columns=["Query"])
        for k in range(banyakkolom):
            indeks = sim_sorted[k][0]
            vecdat = df.loc[:, indeks].values
            tabterm.insert(k+1,"D"+str(k+1),vecdat,True)

    return render_template('index.html',query=q1,sim_sorted=sim_sorted,title=title,short_desc=short_desc,urls=urls,banyakkata=banyakkata,tables=[tabterm.to_html(classes='table')])

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
  app.run(debug=0)
