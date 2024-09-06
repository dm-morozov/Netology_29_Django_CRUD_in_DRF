# Django CRUD with DRF

## Описание проекта

Этот проект демонстрирует создание RESTful API с использованием Django и Django REST Framework (DRF). Основная цель проекта — создание и управление комментариями с возможностью фильтрации, поиска, сортировки и пагинации данных.

## Структура проекта

- `crud_app/` — основное приложение проекта.
    - `models.py` — определение модели `Comment`.
    - `serializers.py` — сериализатор для модели `Comment`.
    - `views.py` — представление для обработки запросов к модели `Comment`.
- `crud_project/` — корневой проект Django.
    - `urls.py` — маршруты URL для API и административной панели.

## Настройки

### `settings.py`

```python
MEDIA = BASE_DIR.joinpath('media')
MEDIA_URL = '/media/'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 3,
    'SEARCH_PARAM': 'search',
    'ORDERING_PARAM': 'ordering',
}

```

### Пагинация

- **Класс пагинации**: `PageNumberPagination`
- **Размер страницы**: 3 элемента

## Модель

### `models.py`

```python
from django.contrib.auth.models import User
from django.db import models

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

```

## Сериализатор

### `serializers.py`

```python
from rest_framework import serializers
from .models import Comment

class CommentSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']

    def forbidden_word(self) -> list:
        return ['test', 'тест', 'тестовый', 'тестовое', 'тестовая', 'тестовые', 'тестовых']

    def validate_text(self, value):
        words = value.split()
        for word in self.forbidden_word():
            if word in words:
                raise serializers.ValidationError(f"Запрещенное слово '{word}'")
        value = value.upper()[:1] + value[1:]
        return value

    def validate(self, attrs):
        if len(attrs['text']) < 10:
            raise serializers.ValidationError('Слишком короткий комментарий')
        return super().validate(attrs)

```

## Представления

### `views.py`

```python
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet
from .models import Comment
from .serializers import CommentSerialiser

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerialiser
    filterset_fields = ['user']  # Поиск по полному совпадению
    search_fields = ['text']  # Поиск по частичному совпадению
    ordering_fields = ['id', 'user', 'text', 'created_at']
    pagination_class = LimitOffsetPagination

```

## URL маршруты

### `urls.py`

```python
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from crud_app.views import CommentViewSet

router = routers.DefaultRouter()
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]

```

## Примеры запросов

### Получить комментарии с фильтрацией и сортировкой

- **URL**: `GET <http://localhost:8000/api/comments/?user=1&ordering=id`>

### Поиск комментариев

- **URL**: `GET <http://localhost:8000/api/comments/?search=Hello&ordering=id`>

### Создать новый комментарий

- **URL**: `POST <http://localhost:8000/api/comments/`>
- **Content-Type**: `application/json`
    
    ```json
    {
        "user": 1,
        "text": "Hello World"
    }
    
    ```
    

### Обновить комментарий

- **URL**: `PUT <http://localhost:8000/api/comments/22/`>
- **Content-Type**: `application/json`
    
    ```json
    {
        "user": 1,
        "text": "Hello World"
    }
    
    ```
    

### Пагинация

- **URL**: `GET <http://localhost:8000/api/comments/?page=2`>

### Пагинация с лимитом и смещением

- **URL**: `GET <http://localhost:8000/api/comments/?limit=2&offset=3`>

## Команды управления

В проекте реализованы две пользовательские команды управления Django для взаимодействия с API комментариев.

### Команда 1: Удаление комментариев

- **Описание**: Эта команда удаляет комментарии с идентификаторами от 1 до 21 (включительно). Команда использует HTTP DELETE запросы к API для удаления каждого комментария по его идентификатору.
- **Файл**: `delete_comments.py`
- **Код**:
    
    ```python
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
    ```
    
- **Использование**:
Запустите команду через Django management команду:
    
    ```
    python manage.py delete_comments
    ```
    

### Команда 2: Обновление текста комментариев

- **Описание**: Эта команда обновляет текст всех комментариев в базе данных. Текст каждого комментария преобразуется в строку с заглавной буквы и остальными буквами в нижнем регистре. Команда также проверяет, что каждый комментарий имеет идентификатор и пользователя, перед отправкой обновления через HTTP PUT запросы.
- **Файл**: `update_comments.py`
- **Код**:
    
    ```python
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
    ```
    
- **Использование**:
Запустите команду через Django management команду:
    
    ```
    python manage.py update_comments
    ```
    

## Чему научились

- Настроили базовое REST API для управления комментариями.
- Реализовали фильтрацию, поиск и сортировку данных.
- Настроили пагинацию для эффективной работы с большими наборами данных.
- Реализовали валидацию данных на уровне сериализатора, включая проверку запрещенных слов и минимальной длины комментария.
- Создали пользовательские команды управления Django для выполнения операций по удалению и обновлению комментариев через API.