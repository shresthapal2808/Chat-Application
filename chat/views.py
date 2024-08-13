from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewUser, Room, Message
from django.http import HttpResponse, JsonResponse


def signup(request):
    if request.method == 'POST':
        first_r = request.POST.get('first_name')
        last_r = request.POST.get('last_name')
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')

        if not first_r or not last_r or not email_r or not password_r:
            messages.error(request, 'All fields are required.')
            return render(request, 'chat/signup.html')

        if NewUser.objects.filter(email=email_r).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'chat/signup.html')  # Redirect to signup to show error message

        user = NewUser(first_name=first_r, last_name=last_r, email=email_r, password=password_r)
        user.save()

        messages.success(request, "Signup successful, please log in")
        return redirect('login')

    else:
        return render(request, 'chat/signup.html')


def login(request):
    if request.method == 'POST':
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')

        try:
            user = NewUser.objects.get(email=email_r)
            if user.password == password_r:
                request.session['user_id'] = user.id
                request.session['username'] = f"{user.first_name} {user.last_name}"
                return redirect('home')
            else:
                messages.error(request, 'Incorrect password.')
        except NewUser.DoesNotExist:
            messages.error(request, 'Email not found.')

        return redirect('login')

    else:
        return render(request, 'chat/login.html')


def home(request):
    if 'user_id' not in request.session:
        return redirect('login')
    return render(request, 'chat/home.html')

def room(request, room):
    if 'user_id' not in request.session:
        return redirect('login')
    username = request.GET.get('username')
    room_details = Room.objects.get(name=room)
    return render(request, 'chat/room.html', {
        'username': username,
        'room': room,
        'room_details': room_details
    })


# to check whether the room is already available or not

def checkview(request):
    if 'user_id' not in request.session:
        return redirect('login')
    room = request.POST['room_name']
    username = request.POST['username']

    if Room.objects.filter(name=room).exists():
        return redirect('/' + room + '/?username=' + username)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/' + room + '/?username=' + username)



def send(request):
    if 'user_id' not in request.session:
        return redirect('login')
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value=message, user=username, room=room_id)
    new_message.save()
    return HttpResponse('Message sent successfully')

def getMessages(request, room):
    if 'user_id' not in request.session:
        return redirect('login')
    room_details = Room.objects.get(name=room)

    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages": list(messages.values())})
