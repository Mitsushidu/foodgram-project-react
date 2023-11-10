from django.db import models
from django.contrib.auth.models import AbstractUser
from .validators import validate_username


class User(AbstractUser):
    username = models.TextField(
        max_length=150,
        validators=(validate_username,),
        unique=True,
        blank=False
    )
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(max_length=254, unique=True, blank=False)
    REQUIRED_FIELDS = ('email', 'first_name', 'last_name')

    class Meta:
        ordering = ('id',)
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=('username', 'email'),
        #         name='unique_user'
        #     )
        # ]

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_follow',
            )
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
