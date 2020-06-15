import datetime
import os
import time
import cv2
import pandas as pd


def recognizeAttendence(dept, sem):
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()  # cv2.createLBPHFaceRecognizer()
    recognizer.read("../trainer" + os.sep + dept + os.sep + sem + os.sep + "Trainner.yml")
    harcascadePath = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    df = pd.read_csv("../StudentDetails" + os.sep + dept + os.sep + sem + os.sep + "StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns = col_names)

    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)
        for(x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x+w, y+h), (225, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y:y+h, x:x+w])

            if(conf < 68):

                find_accuracy.append(100 - int(conf))
                print('conf < 68 --> ' + str(100 - conf))

                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(
                    ts).strftime('%H:%M:%S')
                aa = df.loc[df['Id'] == Id]['Name'].values
                tt = str(Id) + "-" + aa
                attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]

            else:
                Id = 'Unknown'
                tt = str(Id)
            if(conf > 75):

                print('conf > 75 --> ' + str(conf))

                noOfFile = len(os.listdir("../ImagesUnknown"))+1
                cv2.imwrite("../ImagesUnknown" + os.sep + "Image" + str(noOfFile) +
                            ".jpg", im[y:y+h, x:x+w])
            cv2.putText(im, str(tt), (x, y+h), font, 1, (255, 255, 255), 2)
        attendance = attendance.drop_duplicates(subset = ['Id'], keep = 'first')
        cv2.imshow('im', im)
        if (cv2.waitKey(1) == ord('q')):
            print("-> Min value accuracy : ", min(find_accuracy))
            print("-> Max value accuracy : ", max(find_accuracy))
            break
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour, Minute, Second = timeStamp.split(":")
    fileName = "../AttendanceFiles" + os.sep + dept + os.sep + sem + os.sep + "Attendance_" + date + ".csv"
    attendance.to_csv(fileName, index = False)
    cam.release()
    cv2.destroyAllWindows()

    print("Attendance Successfull")
