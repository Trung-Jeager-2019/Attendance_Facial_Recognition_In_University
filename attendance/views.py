from django.shortcuts import render
from django.http import StreamingHttpResponse
import cv2
from django.views.decorators import gzip
from attendance.models import DEPT
# Create your views here.

def index(request):

    context = {
        'depts' : DEPT.objects.all()
    }
    return render(request, 'attendance/attendance.html', context=context)

def add_student(request):
    
    context = {
        'depts' : DEPT.objects.all()
    }
    return render(request, 'attendance/add_student.html', context=context)

'''
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    def __del__(self):
        self.video.release()

    def get_frame(self):
        ret,image = self.video.read()
        ret,jpeg = cv2.imencode('.jpg',image)
        return jpeg.tobytes()

def gen(camera):
    while True:
        frame = camera.get_frame()
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        yield(b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@gzip.gzip_page
def video_feed(request): 
    try:
        return StreamingHttpResponse(gen(VideoCamera()),content_type="multipart/x-mixed-replace;boundary=frame")
    except HttpResponseServerError as e:
        print("aborted")

def stream():
    cap = cv2.VideoCapture(0) 

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: failed to capture image")
            break

        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        cv2.imwrite('demo.jpg', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('demo.jpg', 'rb').read() + b'\r\n')

def video_feed(request):
    return StreamingHttpResponse(stream(), content_type='multipart/x-mixed-replace; boundary=frame')
'''
