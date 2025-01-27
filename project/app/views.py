import re

from uuid import uuid4

from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.core.mail import EmailMessage

from app.models import Category, Donation, Institution, User


class LandingPageView(View):
    def get(self, request):
        bag_count = sum(donation.quantity for donation in Donation.objects.all())
        supported_institutions = sum(1 for institution in Institution.objects.all() if institution.donation_set.all().count() > 0)

        foundations = [foundation for foundation in Institution.objects.filter(type='0')]
        organizations = [organization for organization in Institution.objects.filter(type='1')]
        local_collections = [collection for collection in Institution.objects.filter(type='2')]
        ctx = {
            'bag_count': bag_count,
            'supported_institutions': supported_institutions,
            'foundations': foundations,
            'organizations': organizations,
            'local_collections': local_collections,
        }
        return render(request, 'app/index.html', ctx)


class AddDonationView(LoginRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.all()
        institutions = Institution.objects.all()
        ctx = {
            'categories': categories,
            'institutions': institutions,
        }
        return render(request, 'app/form.html', ctx)


class LoginView(View):
    def get(self, request):
        return render(request, 'app/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_activated:
                    login(request, user)
                    return redirect('landing-page')
                return render(request, 'app/register.html', {'message': "Konto nie zostało jeszcze aktywowane"})
            return redirect('register')
        return render(request, 'app/login.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'app/register.html')

    def post(self, request):
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if name and surname and email and password and password2 and (password == password2) and (User.objects.filter(email=email).exists() is False):
            User.objects.create_user(first_name=name, last_name=surname, email=email, password=password)
            request.session['email'] = email
            return redirect('verification-info')
        else:
            message = 'Proszę wypełnić wszystkie pola, hasło musi być takie same oraz adres email może zostać użyty tylko raz.'
            return render(request, 'app/register.html', {'message': message})


def verification_info(request):
    if request.method == 'GET':
        if 'email' in request.session:
            from_address = "company@gmail.com"
            to_address = request.session.get('email')
            token = str(uuid4())
            url = "http://127.0.0.1:8000/verification/"
            activation_link = f"{url}?activate={token}"
            content = "W celu aktywowania konta proszę kliknąć w poniższy link weryfikacyjny."
            request.session['token'] = token

            email = EmailMessage(
                "Weryfikacja konta",
                f"{content}\n{activation_link}",
                from_email=from_address,
                to=[to_address],
            )
            email.send()

            return render(request, 'app/verification-info.html')
        return redirect('register')


def verification_activate(request):
    if request.method == 'GET':
        activate_token = request.GET.get('activate')
        if activate_token == request.session.get('token') and request.session.get('email'):
            get_user_model()
            user = User.objects.get(email=request.session.get('email'))
            user.is_activated = True
            user.save()
            return render(request, 'app/verified.html')


@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('landing-page')


@login_required(login_url='login')
def donation_confirm_view(request):
    if request.method == 'GET':
        return render(request, 'app/form-confirmation.html')


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'app/profile.html', {'donations': Donation.objects.filter(user=self.request.user).order_by('is_taken')})

    def post(self, request):
        donations_to_update = request.POST.getlist('not_taken')
        for i in donations_to_update:
            donation = Donation.objects.get(pk=i)
            donation.is_taken = True
            donation.save()
        return render(request, 'app/profile.html', {'donations': Donation.objects.filter(user=self.request.user).order_by('is_taken')})


class SettingsView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'app/settings.html')

    def post(self, request):
        if 'button1' in request.POST:
            user = request.user
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            if check_password(password, user.password):
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.save()
                return render(request, 'app/settings.html')
            return render(request, 'app/settings.html', {'message1': 'Niepoprawne hasło'})

        elif 'button2' in request.POST:
            user = request.user
            old_password = request.POST.get('old_pass')
            new_password1 = request.POST.get('new_pass1')
            new_password2 = request.POST.get('new_pass2')
            if check_password(old_password, user.password):
                if new_password1 == new_password2:
                    user.set_password(new_password1)
                    user.save()
                    return redirect('login')
                return render(request, 'app/settings.html', {'message2': 'Hasła różnią się od siebie'})
            return render(request, 'app/settings.html', {'message2': 'Niepoprawne hasło'})


@csrf_exempt
def create_donation(request):
    if request.method == 'POST':
        user = request.user
        bags = request.POST.get('bags')
        raw_categories = request.POST.getlist('categories')
        raw_institution = request.POST.get('organization')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postcode = request.POST.get('postcode')
        phone = request.POST.get('phone')
        date = request.POST.get('date')
        time = request.POST.get('time')
        more_info = request.POST.get('more_info')

        categories = [Category.objects.get(pk=i) for i in raw_categories]

        match = re.search(r'"(.*?)"', raw_institution)
        institution = Institution.objects.get(name=match.group(1))

        donation = Donation.objects.create(
            quantity=bags,
            institution=institution,
            address=address,
            phone_number=phone,
            city=city,
            zip_code=postcode,
            pick_up_date=date,
            pick_up_time=time,
            pick_up_comment=more_info,
            user=user,
            is_taken=False
        )
        donation.categories.set(categories)
        return HttpResponse(status=201)
