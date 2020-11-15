from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import string
import pandas as pd
from collections import Counter
from scipy.sparse import csr_matrix

app = Flask(__name__)

# create stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# create stopword remover
factory2 = StopWordRemoverFactory()
stopword = factory2.create_stop_word_remover()


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

def get_unique_words(articles):
    unique_words = set()

    for article in articles:
        for word in article.split(' '):
            if len(word)>=2:
                unique_words.add(word)
    return sorted(unique_words)


def vectorize(articles,unique_words):
    # Array declaration that will contain unique words from articles

    vocab = {}

    # Get index of the word
    for index, word in enumerate(sorted(list(unique_words))):
        vocab[word] = index

    row,col,val=[],[],[]
    # Getting count values for each vocab word in data
    for id, article in enumerate(articles):
        count_word = dict(Counter(article.split(' ')))

        for word, count in count_word.items():
            if len(word)>=2:
                column_idx = vocab.get(word)
                if column_idx>=0:
                    col.append(id)
                    row.append(column_idx)
                    val.append(count)

    X = (csr_matrix((val,(row,col)), shape=(len(vocab), len(articles)))).toarray()
    df = pd.DataFrame(X, index=sorted(unique_words))
    return df

def vektorquery(query,unique_words):
    query_word=[]
    for word in query.split(' '):
        query_word.append(word)
    vec_query=[0 for i in range (len(unique_words))]
    idx=0
    found = False
    for word in query_word:
        found=False
        idx=0
        while not found and idx<len(unique_words):
            if word==unique_words[idx]:
                vec_query[idx] +=1
                found=True
            idx+=1
    return vec_query

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
  q_vec = vektorquery(q,unique_words)
  
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

def listterm(qkata):
    arrterm=[]
    # membuat array berisi query
    arrterm.append(qkata[0])
    for i in range (1,len(qkata)):
        found = False 
        k = 0
        while (k < len(arrterm) and not(found)):
            if qkata[i] == arrterm[k]:
                found = True
            else:
                k = k+1
        if not(found):
            arrterm.append(qkata[i])
    return arrterm

def kolterm(kata, arrterm):
    q_vec = [0 for i in range (len(arrterm))]
    for j in range (len(kata)):
        for k in range (len(arrterm)):
            if (kata[j] == arrterm[k]):
                q_vec[k] = q_vec[k] + 1
    return(q_vec)   

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

# Get unique words of article
unique_words=get_unique_words(articles)

df = vectorize(articles,unique_words)

# Menyimpan panjang artikel, banyak kata, dan banyak kolom pada variabel
banyakartikel = len(articles)
banyakkolom = len(df.columns)
banyakkata = CountWordsArticles(df)

@app.route('/', methods=['GET','POST'])
def index():
    q1=''
    sim_sorted=[]
    arrterm=[]
    tabterm=pd.DataFrame(data=None, index=None, columns=None)
    if request.method=='POST':
        q1 = request.form['text']
        # Clean query
        q1 = clean_text(q1)
        sim_sorted = get_sorted_sim(q1, df)
        # Showing table of term
        qkata = q1.split()
        arrterm = listterm(qkata)
        q_vec = kolterm(qkata,arrterm)
        tabterm = pd.DataFrame(q_vec, index=arrterm, columns=["Query"])
        for k in range(banyakartikel):
            indeks = sim_sorted[k][0]
            artikel = articles[indeks].split()
            vecdat = kolterm(artikel,arrterm)
            tabterm.insert(k+1,"D"+str(k+1),vecdat,True)

    return render_template('index.html',query=q1,sim_sorted=sim_sorted,title=title,short_desc=short_desc,urls=urls,banyakkata=banyakkata,tables=[tabterm.to_html(classes='table')])

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
  app.run(debug=1)
