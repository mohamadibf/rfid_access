from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import PasswordChangeForm

from .models import RFIDBadge, AccessUser, AccessZone, SystemSettings, Role, CustomUser

User = get_user_model()


# Classe de base pour uniformiser les styles Tailwind
class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_classes = 'w-full px-3 py-2 border rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent'

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update(
                    {'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'})
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': f'{tailwind_classes} bg-white'})
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({'class': f'{tailwind_classes} resize-y'})
            else:
                field.widget.attrs.update({'class': tailwind_classes})
            if field.label:
                field.widget.attrs.update({'placeholder': field.label})


class UserProfileForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }


class PasswordChangeCustomForm(TailwindFormMixin, PasswordChangeForm):
    old_password = forms.CharField(
        label="Ancien mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )
    new_password1 = forms.CharField(
        label="Nouveau mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )
    new_password2 = forms.CharField(
        label="Confirmation",
        widget=forms.PasswordInput(attrs={'placeholder': '••••••••'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].help_text = None


class UserForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(),
        }


class BadgeForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = RFIDBadge
        fields = ['uid', 'is_active']
        widgets = {
            'uid': forms.TextInput(attrs={'placeholder': 'UID du badge'}),
        }


class AccessUserForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = AccessUser
        fields = ['user', 'badge']


class ZoneAccessForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = AccessZone
        fields = ['name', 'description', 'is_restricted']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Description de la zone'
            }),
        }
        labels = {
            'is_restricted': 'Zone restreinte'
        }


class SystemSettingsForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = SystemSettings
        fields = ['enable_time_restrictions', 'opening_time', 'closing_time']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class BadgeSettingsForm(TailwindFormMixin, forms.Form):
    scanning_active = forms.BooleanField(
        label="Mode lecture de badge actif",
        required=False
    )
    badge_uid = forms.CharField(
        label="UID du badge à désactiver",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Entrez l\'UID du badge'})
    )

    def deactivate_badge(self):
        uid = self.cleaned_data.get('badge_uid')
        badge = RFIDBadge.objects.get(uid=uid)
        badge.is_active = False
        badge.save()
        return badge

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded'
            }),
            'permissions': forms.SelectMultiple(attrs={
                'class': 'w-full px-3 py-2 border rounded h-auto'
            })
        }

class UserRoleForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['roles']
        widgets = {
            'roles': forms.SelectMultiple(attrs={
                'class': 'w-full px-3 py-2 border rounded h-auto'
            })
        }