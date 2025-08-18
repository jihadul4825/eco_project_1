from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from cart.views import _cart_id
from cart.models import Cart, CartItem
from cart.utils import transfer_cart

from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

# verification email
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username= email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save() 
            
            # USER ACTIVATION
            
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http',
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send(fail_silently=False)
            login_url = reverse('login')
            return redirect(f"{login_url}?command=verification&email={email}")
    
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            # Transfer cart BEFORE login to preserve session
            transfer_cart(request, user)
            auth.login(request, user)
            return redirect('dashboard')

        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')
            
            
def activate(request, uidb64, token):
    try: 
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        
        # Log user in and transfer cart
        auth.login(request, user)
        transfer_cart(request, user)
        
        
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
        
        
@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')



def logout(request):
    auth.logout(request)
    return redirect('login')


def custom_logout(request):
    # Preserve cart ID before logout
    cart_id = request.session.session_key
    
    # Perform logout
    auth.logout(request)
    
    # Create new session and restore cart ID
    if cart_id:
        # Create new session (this will generate a new session key)
        request.session.create()
        
        # Store the original cart ID in the new session
        request.session['preserved_cart_id'] = cart_id
        request.session.modified = True
    
    return redirect('login')


def forgotPassword(request):   # step 1 for password reset
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset Your Password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if request.is_secure() else 'http',
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('forgotPassword')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')


def resetpassword_validate(request, uid64, token):   # step 2 for password reset
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid  # Store UID for use in reset_password view
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')  # This should be your password reset page
    else:
        messages.error(request, 'This link has expired or is invalid.')
        return redirect('login')


def resetPassword(request):   # step 3 for password reset
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('resetPassword')
        
        uid = request.session.get('uid')
        if not uid:
            messages.error(request, 'Session expired. Please log in again.')
            return redirect('forgotPassword')
        
        try:
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful.')
            request.session.pop('uid',None)
            return redirect('login')
        except Account.DoesNotExist:
            messages.error(request, 'Something went wrong. Please log in again.')
            return redirect('forgotPassword')
        
    return render(request, 'accounts/resetPassword.html')



