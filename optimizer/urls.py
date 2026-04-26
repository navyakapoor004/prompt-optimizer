from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('history/', views.history_view, name='history'),
    path('history/<int:pk>/', views.history_detail, name='history_detail'),
    path('api/optimize/', views.optimize_prompt, name='optimize_prompt'),
    path('api/get-response/', views.get_ai_response, name='get_ai_response'),
    path('api/history/<int:pk>/delete/', views.delete_history, name='delete_history'),
]
