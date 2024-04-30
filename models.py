from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    email = models.CharField(max_length=255, unique=True, verbose_name='Электронная почта')
    phone_number = models.CharField(max_length=255, unique=True, verbose_name='Номер телефона')
    username = models.CharField(max_length=255, unique=True, null=True)
    password = models.CharField(max_length=255, null=True, verbose_name='Пароль')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    # USERNAME_FIELD = phone_number

    def __str__(self):
        return self.first_name + " " + self.last_name + " : " + str(self.pk)


class UserCreateRequest(models.Model):
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    email = models.CharField(max_length=255, unique=True, verbose_name='Электронная почта')
    phone_number = models.CharField(max_length=255, unique=True, verbose_name='Номер телефона')
    username = models.CharField(max_length=255, unique=True, null=True)
    password = models.CharField(max_length=255, null=True, verbose_name='Пароль')
    sms_code = models.CharField(max_length=6, blank=True, null=True)

    class Meta:
        verbose_name = 'Запрос на регистрацию'
        verbose_name_plural = 'Запросы на регистрацию'

    # USERNAME_FIELD = phone_number

    def __str__(self):
        return self.first_name + " " + self.last_name + " : " + str(self.pk)


class Application(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='application')
    # You might want additional fields here to capture more details about the application.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Application for {self.user.username}'

    def calculate_score(self):
        self.score = sum([doc.score for doc in self.documents.all() if doc.status == 'approved'])
        self.save()


class Document(models.Model):
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Pending'),
    ]

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    score = models.IntegerField(default=0, help_text="Score based on the document's importance.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f'{self.title} - {self.status}'
