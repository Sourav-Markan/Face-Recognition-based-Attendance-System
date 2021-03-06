import os
from sys import argv
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename

from src.entities.group import Group
from src.mark_attendance.faceMatcher import FaceMatcher
import cv2

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return filename[-3:].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        data = request.request.get_json()
        
        subject_code = data['subject_code']
        subject_name = data['subject_code']
        
        # If post request has file in it
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                print ('**found file', file.filename)
                filename = secure_filename(file.filename)
                media_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(media_path)

        img=cv2.imread(media_path, cv2.COLOR_BGR2RGB)
        grp=Group(subject_code, subject_name, img)
        Fmatcher=FaceMatcher(grp)
        Fmatcher.process()


    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == '__main__':
    if len(argv) == 2:
        port = int(argv[1])
        print (f"Application is ready and listening to port {port}")
        app.run(host='localhost', port=port, debug=True)
        
    else:
        app.run(host='localhost', port=8080, debug=True)
        print (f"Application is ready and listening to port {port}")