from django.views import View
from django.shortcuts import render, redirect

from app.models import Donation, Institution, User


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


class AddDonationView(View):
    def get(self, request):
        return render(request, 'app/form.html')


class LoginView(View):
    def get(self, request):
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
            return redirect('login')
        else:
            message = 'Proszę wypełnić wszystkie pola, hasło musi być takie same oraz adres email może zostać użyty tylko raz.'
            return render(request, 'app/register.html', {'message': message})
