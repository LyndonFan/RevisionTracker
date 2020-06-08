from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Record(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    study_length = db.Column(db.Integer, default=60)
    comment = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return '<Record %r>' % self.id

@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        new_record = Record(
            subject="Test",
            topic=request.form['content'],
            comment=request.form['notes']
        )

        try:
            db.session.add(new_record)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your record.'
    else:
        records = Record.query.order_by(Record.date_created).all()
        return render_template('index.html',records = records)

@app.route('/delete/<int:id>')
def delete(id):
    record_to_delete = Record.query.get_or_404(id)

    try:
        db.session.delete(record_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that record."

@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    record_to_update = Record.query.get_or_404(id)
    subjects = Record.query.with_entities(Record.subject).distinct()
    topics = Record.query.with_entities(Record.topic).distinct()

    if request.method == 'POST':
        record_to_update.subject = request.form['subject']
        record_to_update.topic = request.form['topic']
        record_to_update.study_length = int(request.form['study_length'])
        y, m, d = request.form['date'].split("-")
        record_to_update.date_created = record_to_update.date_created.replace(year=int(y),month=int(m),day=int(d))
        record_to_update.comment = request.form['comment']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was a problem updating the record."
    else:
        print(subjects)
        print(topics)
        return render_template('update.html',subjects=subjects,topics=topics,record=record_to_update)

if __name__ == "__main__":
    app.run(debug=True)