from django.views import View
from django.shortcuts import render


class LandingPageView(View):
    def get(self, request):
        return render(request, 'app/index.html')


class AddDonationView(View):
    def get(self, request):
        return render(request, 'app/form.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'app/login.html')


class RegisterView(View):
    def get(self, request):
        return render(request, 'app/register.html')
