from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def index_post():
    teks = request.form['text']
    return render_template('index.html',teks=teks)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
  app.run(host='0.0.0.0')
