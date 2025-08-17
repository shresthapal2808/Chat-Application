from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewUser, Room, Message
from django.http import HttpResponse, JsonResponse


def signup(request):
    if request.method == 'POST':
        # Extract data from the form fields; Use request.POST.get('field') for safe access (no error if missing) & 
        # Use request.POST['field'] only if you are sure the field always exists.
        first_r = request.POST.get('first_name')
        last_r = request.POST.get('last_name')
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')
        
        # If any field is missing → show error and reload signup page
        if not first_r or not last_r or not email_r or not password_r:
            messages.error(request, 'All fields are required.')
            return render(request, 'chat/signup.html')
         # Check if a user already exists with the same email
        if NewUser.objects.filter(email=email_r).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'chat/signup.html')  # Redirect to signup to show error message

        # Create and save a new user
        user = NewUser(first_name=first_r, last_name=last_r, email=email_r, password=password_r)
        user.save()

        messages.success(request, "Signup successful, please log in")
        return redirect('login')

    else:
        return render(request, 'chat/signup.html')


def login(request):
    if request.method == 'POST':
        # Get email and password values from the submitted form
        email_r = request.POST.get('email')
        password_r = request.POST.get('password')

        try:
            # Try to fetch user from DB based on entered email
            user = NewUser.objects.get(email=email_r)
            # Check if the entered password matches the saved password in the DB
            if user.password == password_r:
                # If password is correct → save user details in session
                request.session['user_id'] = user.id
                request.session['username'] = f"{user.first_name} {user.last_name}"
                return redirect('home')
            else:
                messages.error(request, 'Incorrect password.')   # If password is wrong → show error message
        # If email does not exist in DB
        except NewUser.DoesNotExist:
            messages.error(request, 'Email not found.')

        return redirect('login')

    else:
        return render(request, 'chat/login.html')

 # Step 1: After login, user lands here → enters room_name + username
def home(request):
    if 'user_id' not in request.session:
        return redirect('login')
    return render(request, 'chat/home.html')

# Step 4: This view runs AFTER checkview redirects user to /<room>/?username=<username>, gets the username & the room from the URL
def room(request, room):
    if 'user_id' not in request.session:
        return redirect('login')
    username = request.GET.get('username')        # username is passed via URL query string
    room_details = Room.objects.get(name=room)    # fetch room object from DB
    return render(request, 'chat/room.html', {
        'username': username,
        'room': room,
        'room_details': room_details
    })

# When a user submits a room name on the home page → this view is triggered.
# to check whether the room is already available or not
# Step 2 + 3: Handles form submission from home page
def checkview(request):
    if 'user_id' not in request.session:
        return redirect('login')
        
    room = request.POST['room_name']      #user-typed room name
    username = request.POST['username']   # user-typed username
    # checks whether the room already exists in the database or not
    if Room.objects.filter(name=room).exists():
        return redirect('/' + room + '/?username=' + username)  # if it exists, redirect the user to that room [e.g,/general/?username=Alice]
    else: 
        new_room = Room.objects.create(name=room)  # if it doesn't exist, create a new room entry in the database
        new_room.save()
        return redirect('/' + room + '/?username=' + username)

''' This function handles sending a new message. It first checks if the user is logged in. Then it takes the message, username, and room ID from the request, 
creates a new Message entry in the database, and finally returns a confirmation response'''
def send(request):
    # ✅ Check if the user is logged in by looking at session data.
    # If not logged in, redirect them to the login page.
    if 'user_id' not in request.session:
        return redirect('login')
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']
    # Model.objects.create() is used to store data in the models, which in turn represents records in your database tables.
    new_message = Message.objects.create(value=message, user=username, room=room_id)  
    new_message.save()
    return HttpResponse('Message sent successfully')


# retrieving the messages from the particular room the user is in. (Just now the user has sent a message, and we need to display it in the UI, so we are fetching
# the messages from that room)
def getMessages(request, room):
    # ✅ Again, check if the user is logged in. Unauthorized users can’t fetch messages.
    if 'user_id' not in request.session:
        return redirect('login')
    room_details = Room.objects.get(name=room)  # finds the room by name

    messages = Message.objects.filter(room=room_details.id) # Fetch all messages linked to that room from the database.
    return JsonResponse({"messages": list(messages.values())}) #Convert the queryset into a list of dictionaries and return as JSON.
