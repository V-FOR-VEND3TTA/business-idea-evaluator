from django.urls import path
from .views import EvaluationWizard, ResultsView, DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('evaluate/new/', EvaluationWizard.as_view(), name='new_evaluation'),
    path('evaluate/step/<int:step>/', EvaluationWizard.as_view(), name='evaluation_step'),
    path('evaluate/results/', ResultsView.as_view(), name='evaluation_results'),
    # Add other URLs for auth, exports, etc.
]