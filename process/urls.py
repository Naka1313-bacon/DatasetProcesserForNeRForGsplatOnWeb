from django.urls import path
from . import views

urlpatterns = [
    # 既存のパターン
    path('', views.upload, name='upload'),
    path('download/<str:unique_folder_name>/', views.download_zip, name='download_zip'),
]