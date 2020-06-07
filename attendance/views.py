from django.shortcuts import render, redirect
from attendance.models import DEPT, SEM, Student, Attendance
from django.contrib import messages
from PIL import Image, ImageTk
import os, os.path
import pandas as pd
import numpy as np
import shutil
import json
import cv2
import csv
import glob
import datetime
import time


# Create your views here.


def index(request):
    context = {
        'depts' : DEPT.objects.all(),
        'sems' : SEM.objects.all()
    }
    return render(request, 'attendance/attendance.html', context = context)


def add_student(request):
    context = {
        'depts' : DEPT.objects.all(),
        'sems' : SEM.objects.all()
    }
    return render(request, 'attendance/add_student.html', context = context)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False

def checkId(Id, dept, sem):

    print("ID: ", Id)

    fileName = 'StudentDetails/' + dept + '/' + sem + "/" + 'StudentDetails.csv'
    # file1=pd.read_csv(fileName)
    Ids = []
    File_student = open(fileName,'rU')
    
    for Student in File_student:
        cells = Student.split(",")
        Ids.append(cells[0])
    File_student.close()
    
    if Id in Ids:
        return False
    else:
        return True

def dataset_creator(request):
    if request.method == 'POST':
        Id = request.POST['id']
        name = request.POST['name']
        dept = request.POST['DEPT'].split(' ', 1)[0]
        # sem = request.POST['SEM'].split(' ', 1)[0]
                
        if is_number(Id) and name.isalpha():
            if checkId(Id, dept, str(1)):
                cam = cv2.VideoCapture(0)
                harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                detector = cv2.CascadeClassifier(harcascadePath)
                sampleNum = 0
                while(True):
                    ret, img = cam.read()
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    faces = detector.detectMultiScale(gray, 1.3, 5)
                    for (x,y,w,h) in faces:
                        
                        cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)        

                        sampleNum = sampleNum + 1
                        for count in range(1, 4):
                            cv2.imwrite("TrainingImage/" + dept + "/" + str(count) + "/" + name + "." + Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])

                        cv2.imshow('frame',img)

                    if cv2.waitKey(100) & 0xFF == ord('q'):
                        break

                    elif sampleNum == 60:
                        break
                cam.release()
                cv2.destroyAllWindows()
                # res = "Images Saved for ID : " + Id +" Name : "+ name
                row = [Id , name]
                
                for count in range(1, 4):
                    with open('StudentDetails/' + dept + '/' + str(count) + "/" + 'StudentDetails.csv','a+') as csvFile:
                        writer = csv.writer(csvFile)
                        writer.writerow(row)
                    csvFile.close()

                # Training image
                # trainer

                response = redirect('/attendance/add-student/')
            else:
                text_error = []
                text_error.append('- ID: ' + Id + ' has already exists.')
                context = {
                    'code_error': '404. That\'s an error.',
                    'text_error': text_error,
                }
                return render(request,'attendance/404_result.html', context=context)
        else:
            text_error = []
            if is_number(Id):
                text_error.append('- Your Name: ' + name + ' must be Alphabetical.')
            elif name.isalpha():
                text_error.append('- Your ID: ' + Id + ' must be Numeric.')
            else:
                text_error.append('- Your Name: ' + name + ' must be Alphabetical.')
                text_error.append('- Your ID: ' + Id + ' must be Numeric.')
            context = {
                'code_error': '404 Not Found',
                'text_error': text_error,
            }
            return render(request,'attendance/404_result.html', context=context)
    return response

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faces = []
    Ids = []
    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        imageNp  =np.array(pilImage,'uint8')
        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces.append(imageNp)
        Ids.append(Id)
    return faces, Ids

# def remove_img(img_name):
#     os.remove(img_name)
#     # check if file exists or not
#     if os.path.exists(img_name) is false:
#         # file did not exists
#         return True

# def remove_all_image(path, length_path): # ------------- Chưa hoàn thành
#     count = 0
#     for name_image in os.listdir(path + '/'):
#         count += 1
#         if name_image.endswith('.jpg'):
#             remove_img('Image' + str(count) +'.jpg')
#             if count == length_path:
#                 break

# def remove_all_image(path):
#     for i in glob.glob(path + '/' + '*.png'):
#         os.remove(i)

def trainer(dept, sem):

    # Delete all image
    # length_path = len([file for file in os.listdir('ImagesUnknown/') if file.endswith('.jpg')])
    # print(length_path)
    # remove_all_image('ImagesUnknown', length_path)

    recognizer = cv2.face_LBPHFaceRecognizer.create()
    # recognizer = cv2.createLBPHFaceRecognizer()
    harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(harcascadePath)
    for count in range(1, 4):
        faces, Id = getImagesAndLabels("TrainingImage/" + dept + "/" + str(count))
        recognizer.train(faces, np.array(Id))
        recognizer.save("trainer/" + dept + "/" + str(count) + "/" + "Trainner.yml")
    print("Images Trained")

def detector(request):
    if request.method == 'POST':

        dept = request.POST.get('DEPT').split(' ', 1)[0]
        sem = request.POST.get('SEM').split(' ', 1)[0]

        dept_name = request.POST.get('DEPT').split(' ', 2)[2]
        sem_name = request.POST.get('SEM').split(' ', 2)[2]
        print(dept_name)
        print(sem_name)

        trainer(dept, sem)
        
        recognizer = cv2.face_LBPHFaceRecognizer.create()#cv2.createLBPHFaceRecognizer()
        recognizer.read("trainer/" + dept + "/" + sem + "/" + "Trainner.yml")
        harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(harcascadePath);
        df=pd.read_csv("StudentDetails/" + dept + "/" + sem + "/" + "StudentDetails.csv")
        cam = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX        
        col_names =  ['Id', 'Name', 'Date', 'Time']
        attendance = pd.DataFrame(columns = col_names)
# -----------------------------------------------------------------------------------------------------------------
        find_accuracy = []
        while True:
            ret, im = cam.read()
            gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2, 5)    

            for(x,y,w,h) in faces:
                cv2.rectangle(im, (x,y),(x+w, y+h),(225, 0, 0),2)
                Id, conf = recognizer.predict(gray[y:y+h, x:x+w])  
                                                
                if(conf < 68):

                    find_accuracy.append(100 - int(conf))
                    print('conf < 68 --> ' + str(100 - conf))

                    ts = time.time()
                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    # print(date)
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    # print(timeStamp)
                    aa = df.loc[df['Id'] == Id]['Name'].values
                    tt = str(Id) + "-" + str(aa)
                    attendance.loc[len(attendance)] = [Id, str(aa[0]), date, timeStamp]

                else:
                    Id = 'Unknown'                
                    tt = str(Id)  
                
                if(conf > 75): # 40

                    # find_accuracy.append(int(conf))
                    print('conf > 75 --> ' + str(conf))

                    noOfFile = len(os.listdir("ImagesUnknown")) + 1
                    cv2.imwrite("ImagesUnknown\Image" + str(noOfFile) + ".jpg", im[y : y+h,x : x+w])            
                cv2.putText(im, str(tt), (x, y+h), font, 1,(255, 255, 255), 2)  
                
            attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
            
            cv2.imshow('im',im) 
            if (cv2.waitKey(1)==ord('q')):

                print("-> Min value accuracy : ", min(find_accuracy))
                print("-> Max value accuracy : ", max(find_accuracy))

                break   

        ts = time.time()      
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour, Minute, Second = timeStamp.split(":")

        fileName_AttendanceFiles = "AttendanceFiles/" + dept + "/" + sem + "/" + "Attendance_" + date + ".csv"
        attendance.to_csv(fileName_AttendanceFiles, index=False)
# -----------------------------------------------------------------------------------------------------------------
        File_AttendanceFiles = open(fileName_AttendanceFiles,'rU')
        List_Attendance = []
        for line in File_AttendanceFiles:
            cells = line.split(",")
            if cells[0] == 'Id':
                continue
            else:
                List_Attendance.append(cells)
        
        total_present = len(List_Attendance)
        print("Student present: ", total_present)
        File_AttendanceFiles.close()
# -----------------------------------------------------------------------------------------------------------------
        fileName_StudentDetails = 'StudentDetails/' + dept + "/" + sem + "/" + 'StudentDetails.csv'
        File_StudentDetails = open(fileName_StudentDetails,'rU')
        List_Student = []
        for line in File_StudentDetails:
            cells = line.split(",")
            
            if cells[0].isalpha() or len(cells) == 1:
                continue
            else:
                List_Student.append(cells)

        total_student = len(List_Student)
        print("Student total: ", total_student)

        File_StudentDetails.close()
# -----------------------------------------------------------------------------------------------------------------
        Numerical_order = list(range(1, int(len(List_Student) + 1)))
        Id_Attendance = []
        Name_Attendance = []
        Date_Attendance = []
        Time_Attendance = []
        Status_Attendance = []

        Dir_Attendance = {}
        for Student_Attendance in List_Attendance:
            Dir_Attendance[Student_Attendance[0]] = Student_Attendance
        print(Dir_Attendance)

        for Student_ in List_Student:
            if Student_[0] in Dir_Attendance.keys():

                Id_Attendance.append(Dir_Attendance[Student_[0]][0])

                Full_Name = Student.objects.filter(id_student = Dir_Attendance[Student_[0]][0])
                Name_Attendance.append(Full_Name[0].full_name_student)
                
                Date_Attendance.append(Dir_Attendance[Student_[0]][2])
                Time_Attendance.append(Dir_Attendance[Student_[0]][3])

                Status_Attendance.append('P')

            else:

                Id_Attendance.append(Student_[0])

                Full_Name = Student.objects.filter(id_student = Student_[0])
                Name_Attendance.append(Full_Name[0].full_name_student)
                
                Date_Attendance.append("--/--/--")
                Time_Attendance.append("--:--:--")

                Status_Attendance.append('A')

        table_attendance = list(zip(Numerical_order, Id_Attendance, Name_Attendance, Date_Attendance, Time_Attendance, Status_Attendance))

        for student in table_attendance:
            if student[5] == 'P':
                id_student_attendance = student[1]
                date_attendance = student[3]
                time_attendance = student[4]
                Attendance.objects.create(id_student = id_student_attendance, DEPT = dept, SEM = sem, date = date_attendance, time = time_attendance)
# -----------------------------------------------------------------------------------------------------------------
        cam.release()
        cv2.destroyAllWindows()

        length_lesson = 0
        for count in range(1, 4):
            DIR = "AttendanceFiles/" + dept + "/" + str(count) + "/"
            length_lesson += len([length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))])

        total_absent = total_student - total_present
        print("Student absent: ", total_absent)

        Statistical_total_present = int((total_present/total_student) * 100)
        Statistical_total_absent = int(100 - Statistical_total_present)

        context = {
            'Statistical_total_present': Statistical_total_present,
            'Statistical_total_absent': Statistical_total_absent,

            'table_attendance': table_attendance,
            'length_lesson': length_lesson,

            'total_present': total_present,
            'total_student': total_student,
            'total_absent': total_absent,

            'dept_name': dept_name,
            'sem_name': sem_name,
            'date': date,
        }
    return render(request,'attendance/result.html', context = context)

def search_attendance(request):
    context = {
        'depts' : DEPT.objects.all(),
        'sems' : SEM.objects.all()
    }
    return render(request, 'attendance/search_attendance.html', context = context)

def search_attendance_details(request):
    if request.method == 'POST':
        
        dept = request.POST.get('DEPT').split(' ', 1)[0]
        sem = request.POST.get('SEM').split(' ', 1)[0]
        
        dept_name = request.POST.get('DEPT').split(' ', 2)[2]
        sem_name = request.POST.get('SEM').split(' ', 2)[2]
        print(dept_name)
        print(sem_name)
        
        format_date = request.POST.get('date').split('-')
        # list_date = datetime.datetime(int(format_date[0]), int(format_date[1]), int(format_date[2]))

        string_date = str(datetime.datetime(int(format_date[0]), int(format_date[1]), int(format_date[2])))
        date = string_date.split(' ', 1)[0]

        fileName_AttendanceFiles = "AttendanceFiles/" + dept + "/" + sem + "/" + "Attendance_" + date + ".csv"
# -----------------------------------------------------------------------------------------------------------------
        File_AttendanceFiles = open(fileName_AttendanceFiles,'rU')
        List_Attendance = []
        for line in File_AttendanceFiles:
            cells = line.split(",")
            if cells[0] == 'Id':
                continue
            else:
                List_Attendance.append(cells)
        
        total_present = len(List_Attendance)
        print("Student present: ", total_present)
        
        File_AttendanceFiles.close()
# -----------------------------------------------------------------------------------------------------------------
        fileName_StudentDetails = 'StudentDetails/' + dept + "/" + sem + "/" + 'StudentDetails.csv'
        File_StudentDetails = open(fileName_StudentDetails,'rU')
        List_Student = []
        for line in File_StudentDetails:
            cells = line.split(",")
            
            if cells[0].isalpha() or len(cells) == 1:
                continue
            else:
                List_Student.append(cells)

        total_student = len(List_Student)
        print("Student total: ", total_student)

        File_StudentDetails.close()
# -----------------------------------------------------------------------------------------------------------------
        Numerical_order = list(range(1, int(len(List_Student) + 1)))
        Id_Attendance = []
        Name_Attendance = []
        Date_Attendance = []
        Time_Attendance = []
        Status_Attendance = []

        Dir_Attendance = {}
        for Student_Attendance in List_Attendance:
            Dir_Attendance[Student_Attendance[0]] = Student_Attendance
        print(Dir_Attendance)

        for Student_ in List_Student:
            if Student_[0] in Dir_Attendance.keys():

                Id_Attendance.append(Dir_Attendance[Student_[0]][0])

                Full_Name = Student.objects.filter(id_student = Dir_Attendance[Student_[0]][0])
                Name_Attendance.append(Full_Name[0].full_name_student)
                
                Date_Attendance.append(Dir_Attendance[Student_[0]][2])
                Time_Attendance.append(Dir_Attendance[Student_[0]][3])

                Status_Attendance.append('P')

            else:

                Id_Attendance.append(Student_[0])

                Full_Name = Student.objects.filter(id_student = Student_[0])
                Name_Attendance.append(Full_Name[0].full_name_student)
                
                Date_Attendance.append("--/--/--")
                Time_Attendance.append("--:--:--")

                Status_Attendance.append('A')

        table_attendance = list(zip(Numerical_order, Id_Attendance, Name_Attendance, Date_Attendance, Time_Attendance, Status_Attendance))

        for student in table_attendance:
            if student[5] == 'P':
                id_student_attendance = student[1]
                date_attendance = student[3]
                time_attendance = student[4]
                Attendance.objects.create(id_student = id_student_attendance, DEPT = dept, SEM = sem, date = date_attendance, time = time_attendance)

        length_lesson = 0
        for count in range(1, 4):
            DIR = "AttendanceFiles/" + dept + "/" + str(count) + "/"
            length_lesson += len([length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))])

        total_absent = total_student - total_present
        print("Student absent: ", total_absent)

        Statistical_total_present = int((total_present/total_student) * 100)
        Statistical_total_absent = int(100 - Statistical_total_present)

        context = {
            'Statistical_total_present': Statistical_total_present,
            'Statistical_total_absent': Statistical_total_absent,

            'table_attendance': table_attendance,
            'length_lesson': length_lesson,

            'total_present': total_present,
            'total_student': total_student,
            'total_absent': total_absent,

            'dept_name': dept_name,
            'sem_name': sem_name,
            'date': date,
        }

    return render(request, 'attendance/result.html', context = context)

def search_individual(request):
    context = {
            'ids': Student.objects.all(),
            'depts': DEPT.objects.all()
    }
    return render(request,'attendance/search_individual.html', context = context)

def search_individual_details(request):
    if request.method == 'POST':

        id_student = request.POST['ID'].split(' ', 1)[0]
        dept = request.POST.get('DEPT').split(' ', 1)[0]

        dept_name = request.POST.get('DEPT').split(' ', 2)[2]
        print(dept_name)

        full_name = str(Student.objects.filter(id_student = id_student)[0]).split(' ', 2)[2]

        Student_Attendance = Attendance.objects.filter(id_student = id_student, DEPT = dept)

        # Danh sách môn buổi ngày giờ học
        Table_Attendance = []
        for Student_ in Student_Attendance:
            cells = str(Student_).split(' - ')

            print('before - ', cells[2])
            Name_Sessions = SEM.objects.filter(code_sem = cells[2])
            cells[2] = Name_Sessions[0].after_sem
            print('after - ', cells[2])
            print(cells)

            Table_Attendance.append(cells)
        print(Table_Attendance)
        total_present = len(Table_Attendance)

        # Số buổi học
        length_lesson = 0
        for count in range(1, 4):
            DIR = "AttendanceFiles/" + dept + "/" + str(count) + "/"
            length_lesson += len([length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))])
        print(length_lesson)
        total_classes = length_lesson

        total_absent = total_classes - total_present

        Statistical_total_present = int((total_present/total_classes) * 100)
        Statistical_total_absent = int(100 - Statistical_total_present)

        context = {
            'Statistical_total_present': Statistical_total_present,
            'Statistical_total_absent': Statistical_total_absent,

            'table_attendance': Table_Attendance,

            'total_present': total_present,
            'total_classes': total_classes,
            'total_absent': total_absent,

            'id_student': id_student,
            'full_name': full_name,
            'dept_name': dept_name,
        }
        
    return render(request,'attendance/search_individual_details.html', context=context)


# class VideoCamera(object):
#     def __init__(self):
#         self.video = cv2.VideoCapture(0)
#     def __del__(self):
#         self.video.release()

#     def get_frame(self):
#         ret,image = self.video.read()
#         ret,jpeg = cv2.imencode('.jpg',image)
#         return jpeg.tobytes()

# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#         yield(b'--frame\r\n'
#         b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# @gzip.gzip_page
# def video_feed(request): 
#     try:
#         return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
#     except HttpResponseServerError as e:
#         print("aborted")

# def stream():
#     cap = cv2.VideoCapture(0) 

#     while True:
#         ret, frame = cap.read()

#         if not ret:
#             print("Error: failed to capture image")
#             break

#         gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

#         cv2.imwrite('demo.jpg', gray)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')

# def video_feed(request):
#     return StreamingHttpResponse(stream(), content_type='multipart/x-mixed-replace; boundary=frame')

