from datetime import datetime

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' ## 3 slashes relative path, 4 slashes absolute path
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' %self.id

@app.route('/', methods=['POST', 'GET'])
def index():
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
        return render_template("index.html", tasks = tasks)
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

if __name__ == "__main__":
    app.run(debug=True)


