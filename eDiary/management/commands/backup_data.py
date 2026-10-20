import json
from datetime import datetime
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from eDiary.models import Category, Notes, Noteshistory, Signup


class Command(BaseCommand):
    help = 'Export users/categories/notes to a JSON backup file (no password hashes beyond Django defaults).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--out',
            default='',
            help='Output path (default: backups/ediary-YYYYMMDD-HHMMSS.json)',
        )

    def handle(self, *args, **options):
        out = options['out']
        if not out:
            folder = Path('backups')
            folder.mkdir(exist_ok=True)
            stamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
            out = str(folder / f'ediary-{stamp}.json')

        payload = {
            'exported_at': datetime.utcnow().isoformat() + 'Z',
            'users': [],
            'signups': [],
            'categories': [],
            'notes': [],
            'noteshistory': [],
        }

        for u in User.objects.all():
            payload['users'].append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'is_active': u.is_active,
                'date_joined': u.date_joined.isoformat() if u.date_joined else None,
            })

        for s in Signup.objects.all():
            payload['signups'].append({
                'id': s.id,
                'user_id': s.user_id,
                'mobileNumber': s.mobileNumber,
                'email_verified': s.email_verified,
                'onboarding_done': s.onboarding_done,
                'profileImage': str(s.profileImage) if s.profileImage else '',
                'regDate': s.regDate.isoformat() if s.regDate else None,
            })

        for c in Category.objects.all():
            payload['categories'].append({
                'id': c.id,
                'signup_id': c.signup_id,
                'categoryName': c.categoryName,
                'CreationDate': c.CreationDate.isoformat() if c.CreationDate else None,
            })

        for n in Notes.objects.all():
            payload['notes'].append({
                'id': n.id,
                'signup_id': n.signup_id,
                'category_id': n.category_id,
                'noteTitle': n.noteTitle,
                'noteDescription': n.noteDescription,
                'CreationDate': n.CreationDate.isoformat() if n.CreationDate else None,
            })

        for h in Noteshistory.objects.all():
            payload['noteshistory'].append({
                'id': h.id,
                'note_id': h.note_id,
                'signup_id': h.signup_id,
                'noteDetails': h.noteDetails,
                'postingDate': h.postingDate.isoformat() if h.postingDate else None,
            })

        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        self.stdout.write(self.style.SUCCESS(f'Backup written to {out}'))
