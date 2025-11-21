from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
class TimeStamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

class Category(TimeStamp):
    TYPE_CHOICES = (
        ('income_from_main_job', 'درامد از شغل اصلی'),
        ('income', 'درآمد'),
        ('important_expense', 'هزینه ضروری'),
        ('Additional costs', 'هزینه های جانبی'),
        ('savings', 'پس‌انداز/سرمایه‌گذاری'),
    )
    COLORS = (
        ('سبز', '#00A878'),
        ('آبی','#2C73D2' ),
        ('قرمز', '#E94F64'),
        ('نارنجی', '#FF7B29'),
        ('بنفش', '#8E7DBE'),
        ('خاکستری', '#AAB8C2')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='expense')
    color = models.CharField(max_length=100, choices=COLORS, default='Gray')
    default_amount = models.PositiveIntegerField(default=0, null=True, blank=True, help_text='واحد پیش ‌فرض (ریال)')
    is_active = models.BooleanField(default=True)

    class Meta(TimeStamp.Meta):
        ordering = ['name']

    def __str__(self):
        return f'{self.user} {self.category_type}: {self.name}'
