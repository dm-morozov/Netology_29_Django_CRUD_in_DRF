import requests
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Обновляет текст комментариев и требует поле user'

    def handle(self, *args, **kwargs):
        base_url = 'http://localhost:8000/api/comments/'

        try:
            # Получаем все комментарии
            response = requests.get(base_url)
            response.raise_for_status()  # Проверяем успешность запроса
            all_comments = response.json()

            for comment in all_comments:
                comment_id = comment.get('id')
                comment_text = comment.get('text', '').upper()[:1] + comment.get('text', '').lower()[1:]
                comment_user = comment.get('user')  # Получаем пользователя

                # Проверяем, что id, текст и пользователь присутствуют
                if comment_id and comment_text and comment_user:
                    put_url = f'{base_url}{comment_id}/'
                    put_response = requests.put(put_url, json={'text': comment_text, 'user': comment_user})

                    if put_response.status_code == 200:
                        self.stdout.write(self.style.SUCCESS(f'Комментарий {comment_id} обновлен успешно.'))
                    else:
                        self.stdout.write(self.style.ERROR(f'Ошибка при обновлении комментария {comment_id}: {put_response.status_code} {put_response.text}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Комментарий с id {comment_id} не имеет текста, id или пользователя.'))

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при запросе к API: {e}'))
