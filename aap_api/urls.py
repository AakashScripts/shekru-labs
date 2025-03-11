from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from .views import ExcelDataViewSet, DownloadHistoryListView, ExcelDataListView, get_all_data, item_list, delete_null_records, index, download_selected
from .auth_views import login_view, register_view, logout_view
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'items', ExcelDataViewSet, basename='item')  # This creates /api/items/ endpoints
router.register(r'data', ExcelDataViewSet, basename='exceldata')

app_name = 'aap_api'


urlpatterns = [
    # Authentication endpoints
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    
    # Main application views
    path('items/', ExcelDataListView.as_view(), name='item_list'),
    
    # API endpoints
    path('', include(router.urls)),
    
    # File handling endpoints
    path('import-excel/', ExcelDataViewSet.as_view({'post': 'import_excel'}), name='data-import-excel'),
    path('import-zip/', ExcelDataViewSet.as_view({'post': 'import_zip_excel'}), name='data-import-zip-excel'),
    path('download-history/', DownloadHistoryListView.as_view(), name='download_history'),
    path('data/export-excel/', ExcelDataViewSet.as_view({'get': 'export_excel'}), name='data-export-excel'),
    path('task-status/', ExcelDataViewSet.as_view({'get': 'task_status'}), name='task-status'),
    
    # New URL for API data
    path('data/all/', get_all_data, name='get-all-data'),
    
    # Default redirect
    path('', RedirectView.as_view(url='auth/login/', permanent=False)),
    
    # Add this line for home page
    path('home/', index, name='home'),
    
    # New URL for deleting null records
    path('api/delete-null-records/', delete_null_records, name='delete-null-records'),

    # Added index view
    path('', index, name='index'),

    # New URL for downloading selected records
    path('download-selected/', download_selected, name='download-selected'),

    # New URL for login and index with login required
    path('', login_view, name='login'),
    path('index/', login_required(index), name='index'),

    # New URLs for register and login
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
]
