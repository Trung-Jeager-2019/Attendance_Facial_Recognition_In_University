from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from ..models import User
from ..decorators import student_required
from ..forms import  StudentSignUpForm
from django.shortcuts import render
from attendance.models import DEPT, SEM, Student, Attendance
from PIL import Image, ImageTk
from django.contrib import messages
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

@student_required
def search_individual(request):
    context = {
        'ids': Student.objects.all(),
        'depts': DEPT.objects.all()
    }
    return render(request,'classroom/students/search_individual.html', context=context)


@student_required
def search_individual_details(request):
    if request.method == 'POST':
        check_id_student = request.POST['ID'].split(" ", 1)[0]
        check_department = request.POST['DEPT'].split(" ", 1)[0]
        warning_messenger = ""

        if check_id_student == "--" and check_department == "--":
            warning_messenger += "mã số sinh viên, môn học"
            messages.success(request, f'Vui lòng chọn ' + warning_messenger + '!')
            context = {
                'ids': Student.objects.all(),
                'depts': DEPT.objects.all()
            }
            return render(request, 'classroom/students/search_individual.html', context=context)
        else:
            if check_id_student == "--":
                warning_messenger += "mã số sinh viên"
                messages.success(request, f'Vui lòng chọn ' + warning_messenger + '!')
                context = {
                    'ids': Student.objects.all(),
                    'depts': DEPT.objects.all()
                }
                return render(request, 'classroom/students/search_individual.html', context=context)
            if check_department == "--":
                warning_messenger += "môn học"
                messages.success(request, f'Vui lòng chọn ' + warning_messenger + '!')
                context = {
                    'ids': Student.objects.all(),
                    'depts': DEPT.objects.all()
                }
                return render(request, 'classroom/students/search_individual.html', context=context)

        id_student = request.POST['ID'].split(' ', 1)[0]
        print(id_student)
        dept = request.POST.get('DEPT').split(' ', 1)[0]
        print(dept)
        dept_name = request.POST.get('DEPT').split(' ', 2)[2]
        print(dept_name)

        full_name = str(Student.objects.filter(id_student = id_student)[0]).split(' ', 2)[2]

        Student_Attendance = Attendance.objects.filter(id_student = id_student, DEPT = dept)
        print(Student_Attendance)
        # Số buổi đã đi học
        Department_Of_Student = []
        for Student_ in Student_Attendance:
            cells = str(Student_).split(' - ')
            cells.remove(str(id_student))
            print(cells)
            Department_Of_Student.append(cells)
        print(Department_Of_Student)
# -----------------------------------------------------------------------------------------------------------------
        Attendance_Of_Student = {}
        Total_Department = 0
        for count in range(1, 4):
            DIR = "AttendanceFiles" + os.sep + dept + os.sep + str(count) + os.sep
            Attendance_List_Search = [length for length in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,length))]
            Total_Department += len(Attendance_List_Search)
            if len(Attendance_List_Search) is not 0:
                List_Attendance = []
                for Date_Attendance in Attendance_List_Search:
                    List_Attendance.append(Date_Attendance.split('_', 1)[1].split('.', 1)[0])
                Attendance_Of_Student[count] = List_Attendance
            else:
                continue
            print(Attendance_Of_Student)
# -----------------------------------------------------------------------------------------------------------------
        Date_Session_Of_Student = {}
        for Date_Session in Department_Of_Student:
            if int(Date_Session[1]) not in Date_Session_Of_Student.keys():
                Date_Session_Of_Student[int(Date_Session[1])] = []
            Date_Session_Of_Student[int(Date_Session[1])].append(Date_Session[2])
            print(str(Date_Session[1]) + '---' + str(Date_Session_Of_Student[int(Date_Session[1])]))
        print(Date_Session_Of_Student)
# -----------------------------------------------------------------------------------------------------------------
        Numerical_order = list(range(1, Total_Department + 1))
        Sessions_Attendance = []
        Date_Attendance = []
        Time_Attendance = []
        Status_Attendance = []

        for key in Attendance_Of_Student.keys():
            print(key)
            if key in Date_Session_Of_Student.keys():
                # Tồn tại buổi học và ngày
                for Date_ in Attendance_Of_Student[key]:
                    if Date_ in Date_Session_Of_Student[key]:
                        print("Có", Date_)
                        Session = str(SEM.objects.filter(code_sem=key))
                        Session = Session.split(' - ', 1)[1]
                        Sessions_Attendance.append(Session.split('>', 1)[0])
                        Date_Attendance.append(Date_)
                        for Time_ in Department_Of_Student:
                            if str(Time_[1]) == str(key) and str(Time_[2]) == str(Date_):
                                Time_Attendance.append(Time_[3])
                        Status_Attendance.append('Có mặt')
                    else:
                        Session = str(SEM.objects.filter(code_sem=key))
                        Session = Session.split(' - ', 1)[1]
                        Sessions_Attendance.append(Session.split('>', 1)[0])
                        Date_Attendance.append(Date_)
                        Time_Attendance.append("--:--:--")
                        Status_Attendance.append('Vắng mặt')
            else:
                # Không tồn tại buổi học vs ngày
                for Date_ in Attendance_Of_Student[key]:
                    print("Vắng")
                    print("key vắng ", key)
                    Session = str(SEM.objects.filter(code_sem=key))
                    Session = Session.split(' - ', 1)[1]
                    Sessions_Attendance.append(Session.split('>', 1)[0])
                    Date_Attendance.append(Date_)
                    Time_Attendance.append("--:--:--")
                    Status_Attendance.append('Vắng mặt')

        Table_Attendance = list(zip(Numerical_order, Sessions_Attendance, Date_Attendance, Time_Attendance, Status_Attendance))
        print(Table_Attendance)
        # Số buổi đã đi học
        total_present = len(Department_Of_Student)
        # Số buổi của lớp học
        total_classes = len(Table_Attendance)
        # Số buổi đã vắng học
        total_absent = total_classes - total_present
        
        if total_classes == 0:
            # Tỉ lệ phần trăm đã đi học
            Statistical_total_present = int((total_present/1) * 100)
            # Tỉ lệ phần trăm đã vắng học
            Statistical_total_absent = int(100 - Statistical_total_present)
        else:
            # Tỉ lệ phần trăm đã đi học
            Statistical_total_present = int((total_present/total_classes) * 100)
            # Tỉ lệ phần trăm đã vắng học
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
    return render(request,'classroom/students/search_individual_details.html', context = context)
