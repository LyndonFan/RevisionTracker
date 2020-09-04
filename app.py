from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from os import path, walk

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    subject = db.Column(db.String(100), nullable=False)
    topics = db.relationship("Topic",back_populates="subject")
    records = db.relationship("Record",back_populates="subject")

    def __repr__(self):
        return self.subject

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    topic = db.Column(db.String(100), nullable=False)
    subject = db.relationship('Subject',back_populates="topics")
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    records = db.relationship("Record",back_populates="topic")

    def __repr__(self):
        return self.topic

class Record(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    subject = db.relationship('Subject',back_populates='records')
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    topic = db.relationship('Topic',back_populates='records')
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    study_length = db.Column(db.Integer, default=60)
    comment = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return '<Record %r>' % self.id

# Use "CATEGORY" to find pages related to the category.

@app.route('/',methods=['GET','POST'])
def index():
    records = Record.query.order_by(Record.date_created).all()
    subjects = Subject.query.order_by(Subject.subject).all()
    topics = Topic.query.order_by(Topic.topic).all()
    return render_template('index.html',records = records, subjects = subjects, topics = topics)

# CATEGORY: Subjects

@app.route('/add/subject', methods=['GET','POST'])
def prep_subject():
    if request.method == 'POST':
        print("adding subject")
        #try:
        s = request.form['subject']
        print(s)
        existing = Subject.query.filter_by(subject=s).first()
        if existing is None:
            db.session.add(Subject(subject=s))
            db.session.commit()
            return redirect('/')
        else:
            return render_template('newsubject.html', error=True, subject_name = s)
        #except:
            #return "There was a problem trying to add the new subject."
    else:
        return render_template('newsubject.html')

@app.route('/view/subject/<string:s>')
def view_subject(s):
    subject = Subject.query.filter_by(subject=s).first()
    records = Record.query.filter_by(subject=subject).order_by(Record.date_created).all()
    topics = Topic.query.filter_by(subject=subject).all()
    return render_template('viewsubject.html',records = records, subject = subject, topics = topics)

# CATEGORY: Topics

@app.route('/get_topics/<string:subject_name>')
def get_topics(subject_name):
    subject = Subject.query.filter_by(subject=subject_name).first()
    if subject is None:
        return jsonify([])
    else:
        topics = Topic.query.filter_by(subject=subject).all()
        topic_names = [t.topic for t in topics]
        return jsonify(topic_names)

@app.route('/add/topic', methods=['GET','POST'])
def add_topic():
    subjects = Subject.query.order_by(Subject.subject).all()
    if request.method == 'POST':
        print("adding topic(s)")
        #try
        s = request.form["subject"]
        subject = Subject.query.filter_by(subject=s).first()
        ts = []
        ts.append(request.form['topic'])
        print(request.form['topic'])
        print(request.form['topics'])
        ts += request.form['topics'].split(";")
        ts = list(filter(lambda x: len(x)>0, ts))
        print(ts)
        for t in ts:
            existing = Topic.query.filter_by(subject=subject).filter_by(topic=t).first()
            if existing is None:
                db.session.add(Topic(topic=t,subject=subject))
                db.session.commit()
            else:
                return render_template('newtopic.html', error=True, topic_name = t)
        return redirect('/add/topic')
        #except:
        #    return "There was a problem trying to add the new topic."
    else:
        return render_template('newtopic.html', subjects=subjects)

@app.route('/delete/topic/<int:id>')
def delete_topic(id):
    topic_to_delete = Topic.query.get_or_404(id)

    try:
        db.session.delete(topic_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that topic."

@app.route('/view/topic/<string:s>/<string:t>')
def view_topic(s,t):
    subject = Subject.query.filter_by(subject=s).first()
    topic = Topic.query.filter_by(subject=subject,topic=t).first()
    records = Record.query.filter_by(subject=subject,topic=topic).order_by(Record.date_created).all()
    return render_template('viewtopic.html', subject = subject, records = records, topic = topic)


# CATEGORY: Records

@app.route('/add/record', methods=['GET','POST'])
def add_record():
    subjects = Subject.query.order_by(Subject.subject).all()
    if request.method == 'POST':
        print("adding record")
        # try:
        s = request.form["subject"]
        subject = Subject.query.filter_by(subject=s).first()
        t = request.form['topic']
        topic = Topic.query.filter_by(subject=subject).filter_by(topic=t).first()
        dt = datetime.strptime(request.form["date_created"], '%Y-%m-%d')
        print(request.form['study_hour'], type(request.form['study_hour']))
        study_length = int(request.form['study_hour'])*60 + int(request.form['study_min'])
        comment = request.form['comment']
        if not (topic is None):
            db.session.add(Record(subject=subject,topic=topic,date_created=dt,study_length=study_length,comment=comment))
            db.session.commit()
            return render_template('newrecord.html', subjects=subjects, added=True)#redirect('/add/record')
        # except:
        #     return "There was a problem trying to add the new record."
    else:
        return render_template('newrecord.html', subjects=subjects, added=False)

@app.route('/delete/record/<int:id>')
def delete_record(id):
    record_to_delete = Record.query.get_or_404(id)

    try:
        db.session.delete(record_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that record."

@app.route('/update/record/<int:id>', methods=['GET','POST'])
def update(id):
    record_to_update = Record.query.get_or_404(id)
    topics = Topic.query.filter_by(subject=record_to_update.subject).all()

    if request.method == 'POST':
        record_to_update.topic = Topic.query.filter_by(subject=record_to_update.subject, topic=request.form['topic']).first()
        record_to_update.study_length = int(request.form['study_hour']) * 60 + int(request.form['study_min'])
        y, m, d = request.form['date'].split("-")
        record_to_update.date_created = record_to_update.date_created.replace(year=int(y),month=int(m),day=int(d))
        record_to_update.comment = request.form['comment']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was a problem updating the record."
    else:
        print(topics)
        return render_template('update.html',topics=topics,record=record_to_update)

# CATEGORY: Date

@app.route('/view/date/<string:d>')
def view_date(d):
    dt = datetime.strptime(d, '%Y-%m-%d')
    records = Record.query.filter_by(date_created = dt).all()
    return render_template('viewdate.html', date = d, records = records)


if __name__ == "__main__":
    extra_dirs = ['/Users/lyndonf/Desktop/RevisionTracker',]
    extra_files = extra_dirs[:]
    for extra_dir in extra_dirs:
        for dirname, dirs, files in walk(extra_dir):
            for filename in files:
                filename = path.join(dirname, filename)
                if path.isfile(filename):
                    extra_files.append(filename)
    app.run(extra_files=extra_files, debug=True)
    # app.run(debug=True)