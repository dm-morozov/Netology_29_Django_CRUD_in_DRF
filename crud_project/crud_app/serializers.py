from wsgiref import validate

from pyexpat import model
from rest_framework import serializers

from .models import Comment


class CommentSerialiser(serializers.ModelSerializer):

    # text = serializers.CharField(min_length=10)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at']

    def forbidden_word(self) -> list:
        value = ['test', 'тест', 'тестовый', 'тестовое', 'тестовая', 'тестовые', 'тестовых']
        return value
    

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