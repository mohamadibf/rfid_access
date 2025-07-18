from django.urls import path

from . import views
from .views import RoleListView, RoleCreateView, RoleUpdateView, UserRoleUpdateView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('logs/', views.access_logs, name='access_logs'),
    path('logs/export/', views.export_access_logs, name='export_access_logs'),

    path('settings/', views.system_settings, name='system_settings'),
    path('scan-badge/', views.scan_badge, name='scan_badge'),
    path('profile/', views.profile_settings, name='profile_settings'),
    path('roles/', RoleListView.as_view(), name='role_list'),
    path('roles/create/', RoleCreateView.as_view(), name='role_create'),
    path('roles/<int:pk>/edit/', RoleUpdateView.as_view(), name='role_update'),
    path('users/<int:pk>/roles/', UserRoleUpdateView.as_view(), name='user_role_update'),
]
