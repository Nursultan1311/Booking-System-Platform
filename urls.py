from django.urls import path
from .views import *

urlpatterns = [
    path('user_exists', CheckUserView.as_view(), name='check-user-exists'),
    path('registration-request', RegisterRequestView.as_view(), name='registration-request'),
    path('registration-confirm', RegisterView.as_view(), name='registration-request'),
    path('login', LoginView.as_view(), name='login'),
    path('user', UserView.as_view(), name='get-user-info'),
    path('add-document/', AddDocumentView.as_view(), name='add-document'),
    path('update-document/<int:document_id>/', DocumentStatusUpdateView.as_view(), name='update-document'),
    path('application/', ApplicationDetailView.as_view(), name='application-detail'),
    path('application/add-document/', AddDocumentView.as_view(), name='add-document'),
]
