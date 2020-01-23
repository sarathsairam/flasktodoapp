from datetime import datetime
from dateutil.tz import tz
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from selenium import webdriver as wbr
import requests, os
import urllib


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fjqgnilcyhahwt:8d2516abb198867ab61c6780d948a1f8522852207c5a6f827152db39e2207a36@ec2-107-20-185-16.compute-1.amazonaws.com:5432/d65m8eht79jeu1'
##postgres_crudapp :: postgres://rrbmthbpslvucv:f6e31849001e963467a7259a82298c063819fcada95a978d95c32f23b5f53ede@ec2-174-129-255-57.compute-1.amazonaws.com:5432/d70boq7ndrdh4c
##'sqlite:///test.db' ## 3 slashes relative path, 4 slashes absolute path

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(500), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' %self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    # panchang = urllib.request.urlopen('http://www.mypanchang.com/mobilewidget.php?cityname=Hyderabad-AP-India&displaymode=full')
    # todayContent = panchang.read()

    chrome_options = wbr.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    drvr = wbr.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
    urls = "http://www.mypanchang.com/mobilewidget.php?cityname=Hyderabad-AP-India&displaymode=full"
    drvr.get(urls)
    text_table = drvr.find_element_by_tag_name('table')

    remoteIP = request.headers['X-Forwarded-For']
    if request.method == 'POST':
        task_content = request.form['content']
        if not task_content:
            return 'Empty Task!!!'
        new_task = Todo(content = task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'Issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", tasks = tasks,
            currtime = datetime.now(tz.tzlocal()).tzname(),
            remoteIP = remoteIP,
            panchangText = text_table)
            # 
    ## return "Hello World!"


@app.route('/delete/<int:id>')
def delete(id):
    task_to_del = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_del)
        db.session.commit()
        return redirect('/')
    
    except:
        return 'Issue deleting task'


@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
    task_to_update = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task_to_update.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        
        except:
            return 'Issue Updating task'
            
    else:
        return render_template('update.html', task = task_to_update)

def get_country(ip_address):
    try:
        response = requests.get("http://ip-api.com/json/{}".format(ip_address))
        js = response.json()
        country = js['countryCode']
        return country
    except Exception as e:
        return "Unknown"

@app.route('/panchang')
def panchang():
    return render_template('panchang.html')




if __name__ == "__main__":
    app.run(debug=True)



