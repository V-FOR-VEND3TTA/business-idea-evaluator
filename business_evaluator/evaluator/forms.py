from django import forms
from .models import Evaluation

class IdeaNameForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['idea_name']
        widgets = {
            'idea_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'My Awesome Business Idea'
            })
        }

class FactorForm(forms.Form):
    score = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '0',
            'max': '10',
            'class': 'form-range',
            'oninput': 'updateScoreValue(this)'
        }),
        min_value=0,
        max_value=10
    )
    
    def __init__(self, *args, **kwargs):
        self.factor_name = kwargs.pop('factor_name', None)
        self.factor_description = kwargs.pop('factor_description', None)
        super(FactorForm, self).__init__(*args, **kwargs)