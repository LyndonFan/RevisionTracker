# Revision Tracker
TL;DR: A website that helps you track your revision by subject and topic.

# Features
- View your study records all at once, or by subject.
- Add in your study records from the past.
- Edit or delete study sessions.

# Installation
Clone this repo, then run `python3 app.py`.

If the `test.db` file is missing, try running the following with python3 in the terminal:
```
from app import *
db.drop_all()
db.create_all()
```

# Potential Additions
- Viewing by topic
- Statistics summarizing your study progress
- Filter/Sort records by various fields
- A better interface

# Inspiration
I was doing my revision and wanted to track how much time I've spent on each topic and each subject. I initially used Google sheets, but then realised:
a) It was quite troublesome, and
b) Google Sheets wasn't prepared to handle such a large file with multiple dependancies.
(And no, Excel was worse at it.)

So I decided to put my coding into good use.

I first played around with an offline program for a while, but creating a suitable GUI took too long. I then stumbled onto a tutorial of constructing a "Task Master" with Flask, which seemed perfect as a starting point. So after a lot of modification, here we are.
