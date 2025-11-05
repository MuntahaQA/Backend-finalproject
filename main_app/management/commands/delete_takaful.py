from django.core.management.base import BaseCommand
from main_app.models import Program


class Command(BaseCommand):
    help = 'Delete programs containing "takaful" in the name'

    def handle(self, *args, **options):
        programs = Program.objects.filter(name__icontains='takaful')
        
        if programs.exists():
            self.stdout.write(f"Found {programs.count()} program(s) with 'takaful' in name:")
            for p in programs:
                self.stdout.write(f"  - {p.name} (ID: {p.id}, Ministry: {p.ministry_owner})")
            
            # Delete all found programs
            deleted_count = programs.count()
            programs.delete()
            self.stdout.write(
                self.style.SUCCESS(f'\n✓ Successfully deleted {deleted_count} program(s)')
            )
        else:
            self.stdout.write(self.style.WARNING("No programs found with 'takaful' in name"))

