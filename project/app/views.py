from django.views import View
from django.shortcuts import render

from app.models import Donation, Institution


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
