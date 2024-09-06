import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Удаляет комментарии с 3 по 19'

    def handle(self, *args, **kwargs):
        base_url = 'http://localhost:8000/api/comments/'

        all_comments = requests.get(base_url).json()

       
        for comment_id in range(1, 22):
            url = f'{base_url}{comment_id}/'
            response = requests.delete(url)

            if response.status_code == 204:
                self.stdout.write(self.style.SUCCESS(f'Комментарий {comment_id} успешно удален.'))
            else:
                self.stdout.write(self.style.ERROR(f'Ошибка при удалении комментария {comment_id}: {response.status_code} {response.text}'))
