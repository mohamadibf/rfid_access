from django.conf import settings
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.db import models


class RFIDBadge(models.Model):
    uid = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Badge {self.uid} ({'Actif' if self.is_active else 'Inactif'})"


class AccessUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='access_user')
    badge = models.OneToOneField(RFIDBadge, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.badge.uid if self.badge else 'Pas de badge'})"


class AccessZone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_restricted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class SystemSettings(models.Model):
    enable_time_restrictions = models.BooleanField(default=False)
    opening_time = models.TimeField(default='08:00:00')
    closing_time = models.TimeField(default='18:00:00')
    scanning_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "System Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)


class AccessZone(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la zone")
    description = models.TextField(blank=True, verbose_name="Description")
    is_restricted = models.BooleanField(default=False, verbose_name="Accès restreint")

    def __str__(self):
        return self.name


class Role(Group):
    class Meta:
        proxy = True
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    roles = models.ManyToManyField(
        Role,
        verbose_name="rôles",
        blank=True,
        related_name="users"
    )

    def get_permissions(self):
        perms = set()
        for role in self.roles.all():
            perms.update(role.permissions.all())
        return perms


class AccessPermission(Permission):
    class Meta:
        proxy = True
        verbose_name = "Permission d'accès"
        verbose_name_plural = "Permissions d'accès"


class AccessLog(models.Model):
    ACCESS_CHOICES = [
        ('granted', 'Accès autorisé'),
        ('denied', 'Accès refusé'),
    ]

    user = models.ForeignKey(AccessUser, on_delete=models.SET_NULL, null=True, blank=True)
    badge = models.ForeignKey(RFIDBadge, on_delete=models.SET_NULL, null=True, blank=True)
    zone = models.ForeignKey(AccessZone, on_delete=models.SET_NULL, null=True)
    access_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ACCESS_CHOICES)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    access_method = models.CharField(max_length=20, default='RFID')

    class Meta:
        ordering = ['-access_time']

    def get_status_display(self):
        return dict(self.ACCESS_CHOICES).get(self.status, self.status)

    def __str__(self):
        return f"{self.user.user.get_full_name() if self.user else 'Unknown'} - {self.get_status_display()} - {self.access_time}"
