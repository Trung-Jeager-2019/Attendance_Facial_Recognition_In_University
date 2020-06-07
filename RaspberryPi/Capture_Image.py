import csv
import cv2
import os, sys


# counting the numbers


def isNumber(s):
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
# Take image function

def checkId(Id, dept, sem):
    fileName = '../StudentDetails' + os.sep + dept + os.sep + sem + os.sep + 'StudentDetails.csv'
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

def takeImages(Id, name, dept, sem):

    if isNumber(Id) and name.isalpha():
        if checkId(Id, dept, sem):

            cam = cv2.VideoCapture(0)
            harcascadePath = cv2.data.haarcascades + "../haarcascade_frontalface_default.xml"
            detector = cv2.CascadeClassifier(harcascadePath)
            sampleNum = 0

            while(True):
                ret, img = cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = detector.detectMultiScale(gray, 1.3, 5)
                for(x,y,w,h) in faces:
                    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    #incrementing sample number
                    sampleNum += 1
                    #saving the captured face in the dataset folder TrainingImage
                    # cv2.imwrite("./TrainingImage" + os.sep + name + "." + Id + '.' + str(sampleNum) + ".jpg", gray[y:y+h, x:x+w])
                    for count in range(1, 4):
                        cv2.imwrite("../TrainingImage" + os.sep + dept + os.sep + str(count) + os.sep + name + "." + Id + '.' + str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
                    #display the frame
                    cv2.imshow('frame', img)
                #wait for 100 miliseconds
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                # break if the sample number is morethan 100
                elif sampleNum == 60:
                    break
            cam.release()
            cv2.destroyAllWindows()

            # res = "Images Saved for ID : " + Id + " Name : " + name
            row = [Id, name]

            for count in range(1, 4):
                with open('../StudentDetails'+ os.sep + dept + os.sep + str(count) + os.sep + 'StudentDetails.csv', 'a+') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow(row)
                csvFile.close()
        else:
            print("--> " + Id + " already exists - Please try again!")
    else:
        if isNumber(Id):
            print("--> Enter Alphabetical Name!")
        if name.isalpha():
            print("--> Enter Numeric ID!")



