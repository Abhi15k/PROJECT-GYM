from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import connection
from authapp.models import MembershipPlan, Trainer, Enrollment, Gallery, Attendance

# Create your views here.
def Home(request):
    return render(request, "index.html")

# Signup part
def signup(request):
    if request.method == "POST":
        username = request.POST.get('usernumber')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        
        if len(username) != 10:
            messages.info(request, "Invalid Phone Number!")
            return redirect('/signup')
        if pass1 != pass2:
            messages.info(request, "Password is not matching!")
            return redirect('/signup')
        
        try:
            if User.objects.get(username=username):
                messages.warning(request, "Phone Number is already taken")
                return redirect('/signup')
        except User.DoesNotExist:
            pass

        try:
            if User.objects.get(email=email):
                messages.warning(request, "Email is already taken")
                return redirect('/signup')
        except User.DoesNotExist:
            pass

        myuser = User.objects.create_user(username, email, pass1)
        myuser.save()
        messages.success(request, "User is Created Please Login")
        return redirect('/login')

    return render(request, "signup.html")

# Login part
def handlelogin(request):
    if request.method == "POST":
        username = request.POST.get('usernumber') 
        pass1 = request.POST.get('pass1')
        myuser = authenticate(username=username, password=pass1)
        if myuser is not None:
            login(request, myuser)
            messages.success(request, "Login Successful")
            return redirect('/')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect("/login")
    return render(request, "handlelogin.html")

# Logout part 
def handleLogout(request):
    logout(request)
    messages.success(request, "Logout Successful")
    return redirect("/login")

# Contact page
def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('num')
        desc = request.POST.get('desc')

        myquery = "INSERT INTO authapp_contact (name, email, phonenumber, description) VALUES (%s, %s, %s, %s)"

        with connection.cursor() as cursor:
            cursor.execute(myquery, (name, email, number, desc))
            connection.commit()

        messages.info(request, "Thanks for contacting us. We will get back to you soon.")
        return redirect('/contact')

    return render(request, "contact.html")

# Enrollment page
def enroll(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please Login and Try Again")
        return redirect('/login')

    if request.method == "POST":
        user_phone = request.user
        existing_enrollment = Enrollment.objects.filter(PhoneNumber=user_phone).first()
        
        FullName = request.POST.get('FullName')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        DOB = request.POST.get('DOB')
        member = request.POST.get('member')
        trainer = request.POST.get('trainer')
        reference = request.POST.get('reference')
        address = request.POST.get('address')

        if existing_enrollment:
            # If user is already enrolled, update the existing enrollment
            query = """
            UPDATE authapp_enrollment 
            SET FullName = %s, Email = %s, Gender = %s, DOB = %s, SelectMembershipplan = %s, SelectTrainer = %s, Reference = %s, Address = %s
            WHERE PhoneNumber = %s
            """
            with connection.cursor() as cursor:
                cursor.execute(query, (FullName, email, gender, DOB, member, trainer, reference, address, user_phone))
                connection.commit()
            messages.success(request, "Enrollment Updated Successfully")
        else:
            # If user is not enrolled yet, create a new enrollment
            query = """
            INSERT INTO authapp_enrollment (FullName, Email, Gender, PhoneNumber, DOB, SelectMembershipplan, SelectTrainer, Reference, Address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            with connection.cursor() as cursor:
                cursor.execute(query, (FullName, email, gender, user_phone, DOB, member, trainer, reference, address))
                connection.commit()
            messages.success(request, "Thanks For Enrollment")
        
        return redirect('/join')

    Membership = MembershipPlan.objects.all()
    SelectTrainer = Trainer.objects.all()
    context = {"Membership": Membership, "SelectTrainer": SelectTrainer}
    return render(request, "enroll.html", context)

# Gallery page
def gallery(request):
    posts = Gallery.objects.all()
    context = {"posts": posts}
    return render(request, "gallery.html", context)

# Attendance page
def attendance(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Please Login and Try Again")
        return redirect('/login')
    SelectTrainer=Trainer.objects.all()
    context={"SelectTrainer":SelectTrainer}
    if request.method=="POST":
        phonenumber=request.POST.get('PhoneNumber')
        Login=request.POST.get('logintime')
        Logout=request.POST.get('loginout')
        SelectWorkout=request.POST.get('workout')
        TrainedBy=request.POST.get('trainer')
        query=Attendance(phonenumber=phonenumber,Login=Login,Logout=Logout,SelectWorkout=SelectWorkout,TrainedBy=TrainedBy)
        query.save()
        messages.warning(request,"Attendace Applied Success")
        return redirect('/attendance')
    return render(request,"attendance.html",context)

# Profile page
def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please Login and Try Again")
        return redirect('/login')

    user_phone = request.user
    posts = Enrollment.objects.filter(PhoneNumber=user_phone)
    attendance = Attendance.objects.filter(phonenumber=user_phone)
    context = {"posts": posts, "attendance": attendance}
    return render(request, "profile.html", context)
