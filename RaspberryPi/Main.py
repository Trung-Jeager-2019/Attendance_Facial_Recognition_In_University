import os  # accessing the os functions
from Check_Camera import camera
from Capture_Image import takeImages
from Train_Image import trainImages
from Recognize_Attendence import recognizeAttendence


# creating the title bar function

def title_bar():
    os.system('cls')  # for windows

    # title of the program

    print("\t**********************************************")
    print("\t***** Face Recognition Attendance System *****")
    print("\t**********************************************")


# creating the user main menu function

def mainMenu():
    title_bar()
    print()
    print(10 * "*", "WELCOME MENU", 10 * "*")
    print("[1] Check Camera")
    print("[2] Capture Faces")
    # print("[3] Train Images")
    print("[4] Recognize & Attendance")
    print("[5] Auto Mail")
    print("[6] Quit")

    while True:
        try:
            choice = int(input("Enter Choice: "))

            if choice == 1:
                Check_Camera()
                break
            elif choice == 2:
                Capture_Image()
                break
            # elif choice == 3:
            #     Train_Image()
            #     break
            elif choice == 4:
                Recognize_Attendence()
                break
            elif choice == 5:
                os.system("py automail.py")
                break
                mainMenu()
            elif choice == 6:
                print("Thank You")
                break
            else:
                print("Invalid Choice. Enter 1-4")
                mainMenu()
        except ValueError:
            print("Invalid Choice. Enter 1-4\n Try Again")
    exit


# ---------------------------------------------------------
# calling the camera test function from check camera.py file

def Check_Camera():
    camer()
    key = input("Enter any key to return main menu")
    mainMenu()


# --------------------------------------------------------------
# calling the take image function form capture image.py file

def Capture_Image():
    Id = input("Enter Your Id: ")
    name = input("Enter Your Name: ")
    dept = input("Enter Your Department: ")
    sem = input("Enter Your Semester: ")

    takeImages(Id, name, dept, sem)
    key = input("Enter any key to return main menu")
    mainMenu()


# -----------------------------------------------------------------
# calling the train images from train_images.py file

# def Train_Image():
#     trainImages()
#     key = input("Enter any key to return main menu")
#     mainMenu()


# --------------------------------------------------------------------
# calling the recognize_attendance from recognize.py file

def Recognize_Attendence():
    dept = input("Enter Your Department: ")
    sem = input("Enter Your Semester: ")
    
    trainImages(dept, sem)
    recognizeAttendence(dept, sem)
    
    key = input("Enter any key to return main menu")
    mainMenu()


# ---------------main driver ------------------
mainMenu()
