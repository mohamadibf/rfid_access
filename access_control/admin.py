from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import RFIDBadge, AccessUser, AccessLog, AccessZone, SystemSettings

User = get_user_model()


class AccessUserInline(admin.StackedInline):
    model = AccessUser
    can_delete = False
    verbose_name_plural = 'Access Users'
    extra = 0  # Évite d'afficher des formulaires vides supplémentaires
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (AccessUserInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


# Désenregistrer le User seulement s'il est déjà enregistré
if User in admin.site._registry:
    admin.site.unregister(User)

# Enregistrer notre version personnalisée
admin.site.register(User, CustomUserAdmin)


@admin.register(RFIDBadge)
class RFIDBadgeAdmin(admin.ModelAdmin):
    list_display = ('uid', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('uid',)
    readonly_fields = ('created_at',)  # Rend le champ créé_at non modifiable


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'zone', 'access_time', 'status', 'ip_address')
    list_filter = ('status', 'zone', 'access_time')
    search_fields = ('user__user__username', 'badge__uid')
    date_hierarchy = 'access_time'
    readonly_fields = ('access_time',)  # Empêche la modification du timestamp


@admin.register(AccessZone)
class AccessZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short', 'is_restricted')
    list_filter = ('is_restricted',)

    def description_short(self, obj):
        return obj.description[:50] + '...' if obj.description else ''

    description_short.short_description = 'Description'


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Permet seulement d'ajouter des settings s'il n'y en a pas déjà
        return not self.model.objects.exists()