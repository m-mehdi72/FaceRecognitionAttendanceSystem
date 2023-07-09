from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if username == 'live_stream' and password == 'Camera@photage':
                return redirect('attendance:index')  # Redirect to camera page
            elif user.is_superuser:
                return redirect('admin:index')  # Redirect to Django admin panel
            else:
                return redirect('s_panel')  # Redirect to student panel's index view
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')

    else:
        return render(request, 'authenticate/login.html', {})

def student_panel(request):
    return render(request, 'panel/s_panel.html', {})

def live_stream(request):
    return render(request, 'Stream/camera.html', {})
 