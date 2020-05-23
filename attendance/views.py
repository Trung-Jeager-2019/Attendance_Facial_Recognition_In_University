from django.shortcuts import render
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
    return render(request, 'attendance/attendance.html', context=context)


def add_student(request):
    context = {
        'depts' : DEPT.objects.all(),
        'sems' : SEM.objects.all()
    }
    return render(request, 'attendance/add_student.html', context=context)


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


def dataset_creator(request):
    if request.method == 'POST':
        Id=request.POST['id']
        name=request.POST['name']
        dept=request.POST['DEPT'].split(' ', 1)[0]
        sem=request.POST['SEM'].split(' ', 1)[0]
        
        fileName='StudentDetails/'+dept+'/'+sem+'/'+'StudentDetails.csv'
        # file1=pd.read_csv(fileName)
        ID=[]
        f=open(fileName,'rU')
        for line in f:
            cells=line.split(",")
            ID.append(cells[0])
        f.close()
                
        if(is_number(Id) and name.isalpha()):
            cam = cv2.VideoCapture(0)
            harcascadePath = "haarcascade_frontalface_default.xml"
            detector=cv2.CascadeClassifier(harcascadePath)
            sampleNum=0
            while(True):
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for (x,y,w,h) in faces:
                    
                    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)        

                    sampleNum=sampleNum+1

                    cv2.imwrite("TrainingImage/"+dept+"/"+sem+"/"+name +"."+Id +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])

                    cv2.imshow('frame',img)

                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break

                elif sampleNum>60:
                    break
            cam.release()
            cv2.destroyAllWindows()
            res = "Images Saved for ID : " + Id +" Name : "+ name
            row = [Id , name]
            
            with open('StudentDetails/'+dept+'/'+sem+'/'+'StudentDetails.csv','a+') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(row)
            csvFile.close()
        
        context = {
            'id':Id,
            'name':name
        }

    return render(request,'attendance/add_student.html', context)

def getImagesAndLabels(path):
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 
    faces=[]
    Ids=[]

    for imagePath in imagePaths:
        
        pilImage=Image.open(imagePath).convert('L')
        imageNp=np.array(pilImage,'uint8')
        Id = int(os.path.split(imagePath)[-1].split(".")[1])

        faces.append(imageNp)
        Ids.append(Id)

    return faces,Ids

def trainer(dept, sem):
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    # recognizer = cv2.createLBPHFaceRecognizer()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector =cv2.CascadeClassifier(harcascadePath)
    faces,Id = getImagesAndLabels("TrainingImage/"+dept+"/"+sem)
    recognizer.train(faces, np.array(Id))
    recognizer.save("trainer/"+dept+"/"+sem+"/"+"Trainner.yml")
    res = "Image Trained"

def detector(request):
    if request.method == 'POST':

        dept = request.POST.get('DEPT').split(' ', 1)[0]
        sem = request.POST.get('SEM').split(' ', 1)[0]

        dept_name = request.POST.get('DEPT').split(' ', 2)[2]
        sem_name = request.POST.get('SEM').split(' ', 2)[2]
        print(dept_name)

        trainer(dept, sem)
        
        recognizer = cv2.face_LBPHFaceRecognizer.create()#cv2.createLBPHFaceRecognizer()
        recognizer.read("trainer/"+dept+"/"+sem+"/"+"Trainner.yml")
        harcascadePath = "haarcascade_frontalface_default.xml"
        faceCascade = cv2.CascadeClassifier(harcascadePath);
        df=pd.read_csv("StudentDetails/"+dept+"/"+sem+"/"+"StudentDetails.csv")
        cam = cv2.VideoCapture(0)
        font = cv2.FONT_HERSHEY_SIMPLEX        
        col_names =  ['Id','Name','Date','Time']
        attendance = pd.DataFrame(columns = col_names)
        
        while True:
            ret, im =cam.read()
            gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
            faces=faceCascade.detectMultiScale(gray, 1.2,5)    
            for(x,y,w,h) in faces:
                cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
                Id, conf = recognizer.predict(gray[y:y+h,x:x+w])  
                                                
                if(conf <68):
                    ts = time.time()      
                    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    aa=df.loc[df['Id'] == Id]['Name'].values
                    tt=str(Id)+"-"+str(aa)
                    attendance.loc[len(attendance)] = [Id,str(aa[0]),date,timeStamp]
                else:
                    Id='Unknown'                
                    tt=str(Id)  
                
                if(conf > 40):
                    noOfFile=len(os.listdir("ImagesUnknown"))+1
                    cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])            
                cv2.putText(im,str(tt),(x,y+h), font, 1,(255,255,255),2)  
                
            attendance = attendance.drop_duplicates(subset=['Id'],keep='first')
            
            cv2.imshow('im',im) 
            if (cv2.waitKey(1)==ord('q')):
                break   
            
        ts = time.time()      
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour,Minute,Second=timeStamp.split(":")

        fileName_AttendanceFiles = "AttendanceFiles/"+dept+"/"+sem+"/"+"Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"

        attendance.to_csv(fileName_AttendanceFiles,index=False)
        # file1=pd.read_csv(fileName)

        Id_Attendance = []
        Name_Attendance = []
        Date_Attendance = []
        Time_Attendance = []

        File_AttendanceFiles = open(fileName_AttendanceFiles,'rU')

        for line in File_AttendanceFiles:
            cells = line.split(",")
            if cells[0] == 'Id':
                continue
            else:
                Id_Attendance.append(cells[0])
                # Xử lý lấy họ tên từ DB
                Student = Student('', '')
                FullName = Student.objects.filter(id_student=str(cells[0]))
                Name_Attendance.append(FullName[0].full_name_student)
                
                Date_Attendance.append(cells[2])
                Time_Attendance.append(cells[3])

        File_AttendanceFiles.close()

        

        table_attendance = list(zip(Id_Attendance, Name_Attendance, Date_Attendance, Time_Attendance))
        total_present = len(table_attendance)

        print("Student present: " + str(total_present))


        for student in table_attendance:

            Student = Student(student[0], Student.objects.filter(id_student=student[0])[0].full_name_student)
            Attendance.objects.create(
                Student =  Student,
                DEPT = dept,
                SEM = sem,
                date = student[2],
                time = student[3],
            )


        fileName_StudentDetails = 'StudentDetails/'+dept+'/'+sem+'/'+'StudentDetails.csv'
        # a=pd.read_csv(fileName1)


        Id_total = []
        Name_total = []

        File_StudentDetails = open(fileName_StudentDetails,'rU')
        for line in File_StudentDetails:
            cells = line.split(",")
            
            if cells[0].isalpha() or len(cells) == 1:
                continue
            else:
                Id_total.append(cells[0])
                Name_total.append(cells[1])
        File_StudentDetails.close()

        table_student = list(zip(Id_total, Name_total))
        total_student = len(table_student)

        print("Student total: " + str(total_student))

        cam.release()
        cv2.destroyAllWindows()

        # print(attendance)
        # res=attendance
        # total=len(name1)-1

        DIR= "AttendanceFiles/"+dept+"/"+sem+"/"
        length_lesson = len([length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))])
        
        total_absent = total_student - total_present
        print("Student absent: " + str(total_absent))

        Statistical_total_present = int((total_present/total_student)*100)
        Statistical_total_absent = int(100 - Statistical_total_present)

        Students = Student.objects.filter(id_student='17050042')

        for Stu in Students:
            print(Stu.full_name_student)

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
    return render(request,'attendance/result.html', context=context)

def individual(request):
    if request.method == 'POST':

        id=request.POST['ID']
        dept=request.POST['DEPT'].split(' ', 1)[0]
        sem=request.POST['SEM'].split(' ', 1)[0]
        
        
        DIR= "AttendanceFiles/"+dept+"/"+sem+"/"
        len1= len([length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))])
        
        a=[]
        a.append(glob.glob("Attendance/ISE/8/*.csv"))

        list=[]
        list1=[]
        count=0
        print(len(a[0]))

        df=pd.read_csv("StudentDetails/"+dept+"/"+sem+"/"+"StudentDetails.csv")
        
        for i in range(len(a[0])): 		
            list.append(str(a[0][i]))
        for j in range(0,len(list)):
            a=pd.read_csv(list[j])
            f=open(list[j],'rU')
            for line in f:
                cells=line.split(",")
                list1.append(cells[0])
        
        print(list1)
        aa=df.loc[df['Id'] == int(id)]['Name'].values
        
        for k in range(0,len(list1)):
            if(list1[k]==id):
                count+=1
        
        print("The student with  id: "+str(id)+" is present for "+ str(count) +" classes ")
        
        absent=len1-count
        
        context = {
            'depts': DEPT.objects.all(),
            'sems': SEM.objects.all(),
            'attended':count,
            'Overall':len1,
            'id':id,
            'absent':absent,
            'dept_name':dept,
            'sem_name':sem,
            'name':str(aa[0])
        }
        
    return render(request,'attendance/individual.html',context=context)


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

