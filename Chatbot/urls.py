from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('api/', views.chatbot_api, name='chatbot_api'),
    path('upload/', views.upload_file, name='chatbot_upload'),
] 