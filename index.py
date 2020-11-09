from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np
import string

app = Flask(__name__)

# Make a request to the website
web = requests.get('https://www.alodokter.com')

# Create an object to parse the HTML format
soup = BeautifulSoup(web.content,'html.parser')

# Array containing url of each article
urls=[]
# Array containing short description of each article
short_desc=[]
# Array containing the title of articles
title=[]

# Retrieve links
for i in soup.findAll("card-post-index"):
    urls.append("https://www.alodokter.com"+ i.attrs['url-path'])
    short_desc.append(i.attrs['short-description'])
    title.append(i.attrs['title'])

# Make array containing all of articles content
articles=[]
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

print(articles[0])

articles_clean = []
for a in articles:
    # Remove Unicode
    article_test = re.sub(r'[^\x00-\x7F]+', ' ', a)
    # Remove Mentions
    article_test = re.sub(r'@\w+', '', article_test)
    # Lowercase the document
    article_test = article_test.lower()
    # Remove punctuations
    article_test = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', article_test)
    # Lowercase the numbers
    article_test = re.sub(r'[0-9]', '', article_test)
    # Remove the doubled space
    article_test = re.sub(r'\s{2,}', ' ', article_test)
    articles_clean.append(article_test)

# Instantiate a TfidfVectorizer object
vectorizer = TfidfVectorizer()
# It fits the data and transform it as a vector
X = vectorizer.fit_transform(articles_clean)
# Convert the X as transposed matrix
X = X.T.toarray()
# Create a DataFrame and set the vocabulary as the index
df = pd.DataFrame(X, index=vectorizer.get_feature_names())

def get_sorted_sim(q, df):
  # Convert the query become a vector
  q = [q]
  q_vec = vectorizer.transform(q).toarray().reshape(df.shape[0],)
  sim = {}
  # Calculate the similarity
  for i in range(10):
    sim[i] = np.dot(df.loc[:, i].values, q_vec) / np.linalg.norm(df.loc[:, i]) * np.linalg.norm(q_vec)
  
  # Sort the values 
  sim_sorted = sorted(sim.items(), key=lambda x: x[1], reverse=True)
  # Print the articles and their similarity values
  return sim_sorted


@app.route('/', methods=['GET','POST'])
def index():
    q1=''
    sim_sorted=[]
    if request.method=='POST':
        q1 = request.form['text']
        sim_sorted=get_sorted_sim(q1, df)

    return render_template('index.html',query=q1,sim_sorted=sim_sorted,title=title,short_desc=short_desc,urls=urls)

# @app.route('/', methods=['POST'])
# def index_post():
#     teks = request.form['text']
#     return render_template('index.html',teks=teks)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
  app.run(debug=1)
