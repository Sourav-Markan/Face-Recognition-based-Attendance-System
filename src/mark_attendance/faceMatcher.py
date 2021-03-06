# !pip install keras-facenet

import numpy as np
from keras_facenet import FaceNet
from src.face_extract import api as Extractor
from src.mark_attendance.attendanceMarker import AttendanceMarker
from src.mark_attendance.bufferManeger import BufferManeger
from src.entities.student import Student
from src.mark_attendance.buffer_config import *
from src.mark_attendance.bufferArg import BufferArg
from root_config import ROOT_DIR
import cv2
import os
import shutil
threshold = 0.15

class FaceMatcher:


    def __init__(self, grp):
        self.student_list = []
        self.encoded_student_faces = []
        self.encoded_extracted_faces = []
        self.present_students = []
        self.student_images = []
        self.subject_code = grp.getSubjectCode()
        bmArg = BufferArg()
        bmArg.setPath(BUFFER_DIR)
        bmArg.setExpirationTime(EXPIRE_DAYS)
        bmArg.setNumOfSub(NO_OF_SUB)
        bm = BufferManeger(bmArg)
        cur_subject = bm.getSubject(self.subject_code)

        self.student_list = cur_subject.getStudentList()
        group_image = grp.getGroupImage()
        extracted_faces = Extractor.cropFaces(group_image)
        self.saveImages(extracted_faces,self.subject_code,EXTRACTED_IMAGES_SAVE_FOLDER)

        for student in self.student_list:
            self.student_images.append(student.getImage())
        embedder = FaceNet()
        self.student_images = np.array(self.student_images)
        extracted_faces = np.array(extracted_faces)
        self.encoded_student_faces = embedder.embeddings(self.student_images)
        self.encoded_extracted_faces = embedder.embeddings(extracted_faces)

    def process(self):
        for encodedVec in self.encoded_extracted_faces:
            student = self.get_best_match_student(encodedVec)
            if student is not None:
                self.present_students.append(student)

        am = AttendanceMarker()
        success = am.mark_present(self.present_students,self.subject_code)
        print(success)
        return success

    def get_best_match_student(self, extractedVec):
        diff_vec = []
        for studentVec in self.encoded_student_faces:
            dist = np.linalg.norm(studentVec - extractedVec)
            diff_vec.append(dist)
        min_index = diff_vec.index(min(diff_vec))
        print(diff_vec[min_index])
        if diff_vec[min_index] > threshold:    #if a good match
            return self.student_list[min_index]
        else:
            return None

    def saveImages(self,extracted_faces,subCode,loc):
        i = 0
        shutil.rmtree(loc + "/"+str(subCode),ignore_errors=True)
        os.mkdir(loc + "/"+str(subCode))
        for extracted_face in extracted_faces:
            i += 1
            cv2.imwrite(loc +"/"+ str(subCode) + "/img" + str(i) + '.jpg', extracted_face)