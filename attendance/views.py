import cv2
import numpy as np
import face_recognition
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse  # Import StreamingHttpResponse
from .models import Attendance
import os
from attendance.models import Attendance
from datetime import datetime
import threading

# Global variables
# ...

def index(request):
    return render(request, 'attendance/index.html')

def mark_attendance(request):
    path = 'attendance/AttendanceImages'
    images = []
    classNames = []
    myList = os.listdir(path)

    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

    def find_encodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    encodeListKnown = find_encodings(images)
    print('Encoding Complete')

    cap = cv2.VideoCapture(0)
    stop_event = threading.Event()

    def process_frame():
        while not stop_event.is_set():
            success, img = cap.read()
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                print(faceDis)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    name = classNames[matchIndex].upper()
                    print(name)
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 255), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    
                    # Check if the name already exists in the database
                    if not Attendance.objects.filter(name=name).exists():
                        # Save attendance in the database
                        attendance = Attendance(name=name)
                        attendance.save()

            # Display the processed frame in the browser
            ret, jpeg = cv2.imencode('.jpg', img)
            frame_data = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n\r\n')

    # Start the face recognition process in a background thread
    thread = threading.Thread(target=process_frame)
    thread.start()

    return StreamingHttpResponse(process_frame(), content_type='multipart/x-mixed-replace; boundary=frame')

def download_attendance(request):
    # Retrieve attendance data from the database
    attendance_list = Attendance.objects.all()

    # Generate CSV content
    csv_content = 'name,timestamp\n'
    for attendance in attendance_list:
        csv_content += f'{attendance.name},{attendance.timestamp}\n'

    # Prepare the response as a downloadable file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance.csv"'
    response.write(csv_content)

    # Clear the attendance data from the database
    Attendance.objects.all().delete()

    return response

