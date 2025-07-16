from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignupView, CustomLoginView, CustomPasswordChangeDoneView, CustomPasswordChangeView, ProfileView, EvaluationWizard, ResultsView, DashboardView, home

urlpatterns = [
    # path('', home, name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('evaluate/new/', EvaluationWizard.as_view(), name='new_evaluation'),
    path('evaluate/step/<int:step>/', EvaluationWizard.as_view(), name='evaluation_step'),
    path('evaluate/results/', ResultsView.as_view(), name='evaluation_results'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    # Add other URLs for exports, etc.
]