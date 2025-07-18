# management/commands/fresh.py
import os
import shutil
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Réinitialise complètement la base de données comme dans Laravel'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\nDébut de la réinitialisation...\n'))

        # Étape 1: Supprimer uniquement les migrations de vos apps personnalisées
        self.delete_app_migrations()

        # Étape 2: Supprimer la base de données
        self.delete_database()

        # Étape 3: Recréer les migrations
        self.recreate_migrations()

        self.stdout.write(self.style.SUCCESS('\nRéinitialisation terminée avec succès !\n'))

    def delete_app_migrations(self):
        """Supprime uniquement les migrations des apps personnalisées"""
        apps_to_reset = ['access_control']  # Remplacez par le nom de votre app
        base_dir = settings.BASE_DIR

        for app in apps_to_reset:
            migrations_dir = os.path.join(base_dir, app, 'migrations')
            if os.path.exists(migrations_dir):
                for filename in os.listdir(migrations_dir):
                    if filename != '__init__.py' and filename.endswith('.py'):
                        os.remove(os.path.join(migrations_dir, filename))
                self.stdout.write(self.style.SUCCESS(f'Migrations supprimées pour {app}'))

    def delete_database(self):
        """Supprime la base de données SQLite"""
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(self.style.SUCCESS(f'Base de données supprimée: {db_path}'))

    def recreate_migrations(self):
        """Recrée les migrations et applique les migrations de base"""
        try:
            call_command('makemigrations')
            call_command('migrate')
            call_command('createsuperuser', interactive=False)
            self.stdout.write(self.style.SUCCESS('Migrations recréées avec succès'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors des migrations: {e}'))
            raise