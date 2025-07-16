from urllib import request
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib import messages
from django.conf import settings
from .models import Evaluation
from .forms import IdeaNameForm, FactorForm
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordChangeDoneView


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True  # Prevent logged-in users from accessing login page

class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('password_change_done')

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'

class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('dashboard')  # Or your desired redirect
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # Auto-login after signup
        return response

FACTORS = [
    {
        'name': 'urgency',
        'title': 'Urgency',
        'description': 'How badly do people want or need this right now?'
    },
    {
        'name': 'market_size',
        'title': 'Market Size',
        'description': 'How many people are purchasing things like this?'
    },
    {
        'name': 'pricing_potential',
        'title': 'Pricing Potential',
        'description': 'What is the highest price a typical purchaser would be willing to spend?'
    },
    {
        'name': 'cost_of_customer_acquisition',
        'title': 'Cost of Customer Acquisition',
        'description': 'How difficult or expensive is it to acquire customers?'
    },
    {
        'name': 'cost_of_value_delivery',
        'title': 'Cost of Value Delivery',
        'description': 'How expensive or complex is it to deliver the solution?'
    },
    {
        'name': 'uniqueness_of_offer',
        'title': 'Uniqueness of Offer',
        'description': 'How unique or differentiated is the offer?'
    },
    {
        'name': 'speed_to_market',
        'title': 'Speed to Market',
        'description': 'How quickly can you create something to sell?'
    },
    {
        'name': 'upfront_investment',
        'title': 'Upfront Investment',
        'description': 'How much time/money must be invested before selling?'
    },
    {
        'name': 'upsell_potential',
        'title': 'Upsell Potential',
        'description': 'Are there natural follow-up products or upgrades?'
    },
    {
        'name': 'evergreen_potential',
        'title': 'Evergreen Potential',
        'description': 'Will demand remain stable or grow over time?'
    },
]

class DashboardView(LoginRequiredMixin, ListView):
    model = Evaluation
    template_name = 'evaluator/dashboard.html'
    context_object_name = 'evaluations'
    
    def get_queryset(self):
        return Evaluation.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_evaluations'] = self.get_queryset().count()
        
        # Calculate average score
        evaluations = self.get_queryset()
        if evaluations.exists():
            context['average_score'] = sum(e.total_score for e in evaluations) / evaluations.count()
        else:
            context['average_score'] = 0
            
        return context

class EvaluationWizard(TemplateView):
    template_name = 'evaluator/step1.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        step = kwargs.get('step', 1)
        
        if step == 1:
            context['form'] = IdeaNameForm()
        else:
            factor = FACTORS[step-2]
            context['form'] = FactorForm(
                factor_name=factor['title'],
                factor_description=factor['description']
            )
            context['factor'] = factor
            context['evaluation'] = Evaluation.objects.get(
                id=self.request.session.get('evaluation_id')
            )
        
        context['step'] = step
        context['total_steps'] = len(FACTORS) + 1
        context['progress'] = int(((step-1) / context['total_steps']) * 100)
        context['factors'] = FACTORS  # Pass all factors for reference
        
        return context
    
    def post(self, request, *args, **kwargs):
        step = kwargs.get('step', 1)
        evaluation_id = request.session.get('evaluation_id')
        
        if step == 1:
            form = IdeaNameForm(request.POST)
            if form.is_valid():
                evaluation = form.save(commit=False)
                if request.user.is_authenticated:
                    evaluation.user = request.user
                evaluation.save()
                request.session['evaluation_id'] = evaluation.id
                return redirect(reverse('evaluation_step', kwargs={'step': 2}))
        else:
            form = FactorForm(request.POST)
            if form.is_valid():
                evaluation = Evaluation.objects.get(id=evaluation_id)
                factor_name = FACTORS[step-2]['name']
                setattr(evaluation, factor_name, form.cleaned_data['score'])
                evaluation.save()
                
                if step == len(FACTORS) + 1:
                    return redirect('evaluation_results')
                else:
                    return redirect(reverse('evaluation_step', kwargs={'step': step+1}))
        
        return self.render_to_response(self.get_context_data(**kwargs))

class ResultsView(TemplateView):
    template_name = 'evaluator/results.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get evaluation ID from session or query parameter
        evaluation_id = self.request.session.get('evaluation_id') or self.request.GET.get('id')
        
        try:
            evaluation = Evaluation.objects.get(id=evaluation_id)
            # Verify ownership if user is authenticated
            if self.request.user.is_authenticated and evaluation.user != self.request.user:
                raise Evaluation.DoesNotExist
        except Evaluation.DoesNotExist:
            raise Http404("Evaluation not found")
        
        context['evaluation'] = evaluation
        context['factors'] = evaluation.get_factors()
        
        # Result interpretation
        if evaluation.total_score <= 50:
            context['result_message'] = "Move on to another idea. The market is not attractive."
            context['result_class'] = "danger"
        elif evaluation.total_score <= 74:
            context['result_message'] = "Has potential to pay the bills but not a home run without major effort."
            context['result_class'] = "warning"
        else:
            context['result_message'] = "Promising idea. High market attractiveness. Worth pursuing."
            context['result_class'] = "success"
        
        return context

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evaluations'] = Evaluation.objects.filter(user=self.request.user)
        return context

def home(request):
    return render(request, ('evaluator/home.html'))