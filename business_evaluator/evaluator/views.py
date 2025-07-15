from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib import messages
from django.conf import settings
from .models import Evaluation
from .forms import IdeaNameForm, FactorForm

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
        
        context['step'] = step
        context['total_steps'] = len(FACTORS) + 1
        context['progress'] = int(((step-1) / context['total_steps']) * 100)
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
        evaluation_id = self.request.session.get('evaluation_id')
        evaluation = Evaluation.objects.get(id=evaluation_id)
        
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