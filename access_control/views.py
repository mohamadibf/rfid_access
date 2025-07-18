import random

from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse, HttpResponse, response
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib import messages
from django.db.models import Count, Q
from datetime import datetime, timedelta
import csv

from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import UpdateView, CreateView, ListView

from .models import RFIDBadge, AccessUser, AccessLog, AccessZone, SystemSettings, Role, CustomUser
from .forms import UserForm, BadgeForm, ZoneAccessForm, SystemSettingsForm, UserProfileForm, PasswordChangeCustomForm, \
    BadgeSettingsForm, RoleForm, UserRoleForm

User = get_user_model()

@login_required()
def dashboard(request):
    # Today's stats
    today = datetime.now().date()
    today_logs = AccessLog.objects.filter(access_time__date=today)

    # Weekly access data for chart
    week_dates = [(today - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
    week_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = AccessLog.objects.filter(access_time__date=day).count()
        week_data.append(count)

    context = {
        'access_today': today_logs.count(),
        'active_badges': RFIDBadge.objects.filter(is_active=True).count(),
        'alerts': AccessLog.objects.filter(status='denied', access_time__date=today).count(),
        'week_labels': week_dates,
        'week_data': week_data,
        'recent_activity': AccessLog.objects.select_related('user', 'badge', 'zone').order_by('-access_time')[:5]
    }
    return render(request, 'access_control/dashboard.html', context)


@login_required
def profile_settings(request):
    if request.method == 'POST':
        if 'personal_info' in request.POST:
            user_form = UserProfileForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Informations mises à jour')
                return redirect('profile_settings')

        elif 'password_change' in request.POST:
            password_form = PasswordChangeCustomForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Mot de passe changé avec succès')
                return redirect('profile_settings')
    else:
        user_form = UserProfileForm(instance=request.user)
        password_form = PasswordChangeCustomForm(request.user)

    return render(request, 'access_control/profile_settings.html', {
        'user_form': user_form,
        'password_form': password_form
    })

@login_required
def user_management(request):
    users_list = User.objects.all().select_related('access_user').order_by('last_name')

    # Pagination (10 utilisateurs par page)
    paginator = Paginator(users_list, 10)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur ajouté avec succès')
            return redirect('user_management')
    else:
        form = UserForm()

    context = {
        'users': users,
        'form': form
    }
    return render(request, 'access_control/users.html', context)


@login_required
@require_POST
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    messages.success(request, "L'utilisateur a été supprimé avec succès")
    return redirect('user_management')


@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    try:
        access_user = user.access_user
    except User.access_user.RelatedObjectDoesNotExist:
        # Crée un AccessUser si inexistant
        access_user = AccessUser.objects.create(user=user)
        messages.info(request, "Un profil AccessUser a été créé pour cet utilisateur")

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        badge_form = BadgeForm(request.POST, instance=access_user.badge if hasattr(access_user, 'badge') else None)

        if user_form.is_valid() and badge_form.is_valid():
            user_form.save()

            # Gestion du badge
            if badge_form.cleaned_data.get('uid'):
                badge, created = RFIDBadge.objects.get_or_create(
                    uid=badge_form.cleaned_data['uid'],
                    defaults={'is_active': True}
                )
                access_user.badge = badge
                access_user.save()

            messages.success(request, "Utilisateur mis à jour avec succès")
            return redirect('user_management')
    else:
        user_form = UserForm(instance=user)
        badge_form = BadgeForm(instance=access_user.badge if hasattr(access_user, 'badge') else None)

    return render(request, 'access_control/edit_user.html', {
        'user_form': user_form,
        'badge_form': badge_form,
        'user': user,
        'access_user': access_user
    })

@login_required
def access_logs(request):
    logs = AccessLog.objects.select_related('user', 'badge').order_by('-access_time')

    # Filtrage
    date_filter = request.GET.get('date')
    uid_filter = request.GET.get('uid')
    name_filter = request.GET.get('name')
    status_filter = request.GET.get('status')

    if date_filter:
        logs = logs.filter(access_time__date=date_filter)
    if uid_filter:
        logs = logs.filter(badge__uid__icontains=uid_filter)
    if name_filter:
        logs = logs.filter(user__user__first_name__icontains=name_filter) | \
               logs.filter(user__user__last_name__icontains=name_filter)
    if status_filter:
        logs = logs.filter(status=status_filter)

    # Tri
    order_by = request.GET.get('order_by', 'access_time')
    if request.GET.get('desc'):
        order_by = f'-{order_by}'
    logs = logs.order_by(order_by)

    # Pagination
    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page')
    logs_page = paginator.get_page(page_number)

    context = {
        'logs': logs_page,
        'other_params': request.GET.urlencode().replace(f'page={page_number}&', '').replace(f'&page={page_number}',
                                                                                            '').replace(
            f'page={page_number}', '')
    }
    return render(request, 'access_control/logs.html', context)

@login_required
def system_settings(request):
    if request.method == 'POST':
        if request.POST.get('form_type') == 'access_rules':
            form = SystemSettingsForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Règles d'accès mises à jour")

                # Gestion des zones restreintes
                restricted_zones = request.POST.getlist('restricted_zones')
                AccessZone.objects.all().update(is_restricted=False)
                AccessZone.objects.filter(id__in=restricted_zones).update(is_restricted=True)

        elif request.POST.get('form_type') == 'badge_settings':
            badge_form = BadgeSettingsForm(request.POST)
            if badge_form.is_valid():
                if 'deactivate' in request.POST:
                    badge = badge_form.deactivate_badge()
                    messages.success(request, f"Badge {badge.uid} désactivé")
                else:
                    badge_form.save()
                    messages.success(request, "Paramètres badges mis à jour")

    # Récupération des données actuelles
    zones = AccessZone.objects.all()
    return render(request, 'access_control/settings.html', {
        'access_form': SystemSettingsForm(),
        'badge_form': BadgeSettingsForm(),
        'zones': zones
    })

@csrf_exempt
@require_POST
def scan_badge(request):
    try:
        # 1. Récupérer ou simuler l'UID du badge
        simulated_uid = f"SIM{random.randint(1000, 9999)}"  # Simulation
        badge_uid = request.POST.get('uid', simulated_uid)

        # 2. Trouver ou créer le badge
        badge, created = RFIDBadge.objects.get_or_create(
            uid=badge_uid,
            defaults={'is_active': True}
        )

        # 3. Créer le log d'accès
        AccessLog.objects.create(
            user=request.user.access_user if hasattr(request.user, 'access_user') else None,
            badge=badge,
            status='granted',
            details=f"Scan depuis l'interface d'édition (UID: {badge_uid})"
        )

        return JsonResponse({
            'status': 'success',
            'uid': badge_uid,
            'is_new': created,
            'message': 'Badge enregistré et log créé'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('auth.view_role', raise_exception=True), name='dispatch')
class RoleListView(ListView):
    model = Role
    template_name = 'access_control/role_list.html'
    context_object_name = 'roles'

    # The get method is optional since ListView already provides it
    # Only include if you need to add custom logic
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('auth.add_role', raise_exception=True), name='dispatch')
class RoleCreateView(CreateView):
    model = Role
    form_class = RoleForm
    template_name = 'access_control/role_form.html'
    success_url = reverse_lazy('role_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('auth.change_role', raise_exception=True), name='dispatch')
class RoleUpdateView(UpdateView):
    model = Role
    form_class = RoleForm
    template_name = 'access_control/role_form.html'
    success_url = reverse_lazy('role_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('auth.change_user'), name='dispatch')
class UserRoleUpdateView(UpdateView):
    model = CustomUser
    form_class = UserRoleForm
    template_name = 'access_control/user_role_form.html'
    success_url = reverse_lazy('user_list')

def export_access_logs(request):
    # Récupération des paramètres de filtrage
    date_filter = request.GET.get('date')
    uid_filter = request.GET.get('uid')
    name_filter = request.GET.get('name')
    status_filter = request.GET.get('status')

    # Construction de la requête de base
    logs = AccessLog.objects.select_related(
        'user__user',
        'badge',
        'zone'
    ).order_by('-access_time')

    # Application des filtres
    if date_filter:
        logs = logs.filter(access_time__date=date_filter)

    if uid_filter:
        logs = logs.filter(
            Q(badge__uid__icontains=uid_filter) |
            Q(uid__icontains=uid_filter)
        )

    if name_filter:
        logs = logs.filter(
            Q(user__user__first_name__icontains=name_filter) |
            Q(user__user__last_name__icontains=name_filter)
        )

    if status_filter:
        logs = logs.filter(status=status_filter)

    # Configuration de la réponse HTTP
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename="access_logs_export_{timezone.now().strftime("%Y%m%d_%H%M")}.csv"'
        },
    )

    # Création du writer CSV avec gestion d'encodage
    writer = csv.writer(response, delimiter=';')

    # En-têtes des colonnes
    headers = [
        'ID Log',
        'Nom Utilisateur',
        'Email',
        'UID Badge',
        'Zone',
        'Date et Heure',
        'Statut',
        'Détails',
        'Adresse IP',
        'Méthode d\'accès'
    ]
    writer.writerow(headers)

    # Écriture des données
    for log in logs.iterator(chunk_size=1000):
        writer.writerow([
            log.id,
            log.user.user.get_full_name() if log.user else 'Inconnu',
            log.user.user.email if log.user else '',
            log.badge.uid if log.badge else (log.uid or 'N/A'),
            log.zone.name if log.zone else 'Non spécifiée',
            log.access_time.strftime('%Y-%m-%d %H:%M:%S'),
            log.get_status_display(),
            log.details or '',
            getattr(log, 'ip_address', 'N/A'),
            getattr(log, 'access_method', 'RFID') or 'RFID'
        ])

    return response