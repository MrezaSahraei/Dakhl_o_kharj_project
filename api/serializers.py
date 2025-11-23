from django.template.context_processors import request
from rest_framework import serializers
from .models import *
from django.db import IntegrityError

class CategorySerializer(serializers.ModelSerializer):
    #id = serializers.SlugRelatedField(read_only=True)
    #created_at = serializers.DateTimeField(read_only=True)
    #updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Category
        fields =[
            'id', 'name', 'category_type', 'color', 'default_amount', 'is_active'
        ]
        read_only_fields = ['created_at', 'updated_at', 'id']

    def validate_name(self, value): #category name clean
        request = self.context.get('request') #getting request
        user = getattr(request, 'user', None) #getting user
        query_set = Category.objects.select_related('user').none()
        if user and user.is_authenticated:
            query_set = Category.objects.select_related('user').filter(user=user, name=value)
            if self.instance:
                if query_set.exclude(pk=self.instance.pk).exists():
                    raise serializers.ValidationError('از قبل دسته ای با این نام دارید!')
        return value

    def validate_default_amount(self, value): #default_amount clean
        if value and value < 0:
            raise serializers.ValidationError('مبلع پیش فرض نمیتواند منفی باشد!')
        return value

    def create(self,validated_data):
        request = self.context.get('request') #getting request
        user = getattr(request, 'user', None)
        vd = validated_data
        try: # مدیریت خطای دیتابیس هنگام ساخت رکورد جدید
            instance = Category.objects.create(user=user,
                name=vd['name'],
                category_type=vd['category_type'],
                color=vd['color'],
                default_amount=vd['default_amount'],
                is_active=vd['is_active'])
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس بخاطر رکورد تکراری یا نقض محدودیت '})
        return instance

    def update(self, instance, validate_data):
        validate_data.pop('user',None) #Preventing the client from changing the user
        for attr, value in validate_data.items():
            setattr(instance, attr, value)
        try: #مدیریت حطای دیتابیس هنگام اپدیت رکورد
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت دسته'})
        return instance

class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['id', 'user', 'category', 'amount', 'description',
                  'transaction_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value and value < 0:
            raise serializers.ValidationError('مبلع پیش فرض نمیتواند منفی باشد!')

    def validate_category(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and value.user.id != getattr(user, 'id', None):
            raise serializers.ValidationError('دسته انتخاب شده متعلق به شما نیست')
        if value is None:
            raise serializers.ValidationError('دسته ای انتخاب نشده است!')
        if not value.is_active:
            raise serializers.ValidationError('نمیتوانید تراکنشی داشته باشید زیرا این دسته غیرفغال است')

    def create(self,validated_data):
        request = self.context.get('request') #getting request
        user = getattr(request, 'user', None)
        vd = validated_data
        try: # مدیریت خطای دیتابیس هنگام ساخت رکورد جدید
            instance = Transaction.objects.create(user=user,
                category=vd['category'],
                amount=vd['amount'],
                description=vd['description'],
                transaction_date=vd['transaction_date'])
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس هنگام ثبت تراکنش '})
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('user', None) #Preventing the client from changing the user in transactions
        for attr , value in validated_data.items():
            setattr(instance, attr, value)
        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس هنگام اپدیت تراکنش'})

class BudgetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budgeting
        fields = [
            'id','category', 'minimum_target_amount', 'maximum_target_amount',
            'start_date', 'end_date' , 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_categoey(self, value):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and value.user.id != getattr(user, 'id', None):
            raise serializers.ValidationError('دسته انتخاب شده متعلق به شما نیست')
        if value is None:
            raise serializers.ValidationError('دسته ای انتخاب نشده است!')
        return value

    def validate(self, data):
        """
        General checks: start <= end and min <= max and ensuring non-negative values
        """
        def get_final_value(field_name): #for PATCH requests
            new_value = data.get(field_name)

            if new_value is None and self.instance:
                return getattr(self.instance, field_name, None)
            return new_value

        #getting fields from data
        min_amt = data.get('minimum_target_amount')
        max_amt = data.get('maximum_target_amount')
        start = data.get('start_date')
        end = data.get('end_date')

        if min_amt and max_amt and min_amt > max_amt:
            raise serializers.ValidationError('حداکثر بودجه تعیین شده نمیتواند کوچکتر از حداقل بودجه تعیین شده باشد ')

        if (min_amt is not None) and min_amt < 0 or (max_amt is not None) and max_amt < 0:
            raise serializers.ValidationError('مبلع بودجه نمیتواند منفی باشد!')

        if start and end and start > end:
            raise serializers.ValidationError('تارخ پایان نمیتواند کوچکتر از تاریخ شروع باشد')

        return data

    def create(self, validated_data):
        request =self.context.get('request')
        user = getattr(request, 'user', None)
        vd = validated_data
        try: # مدیریت خطای دیتابیس هنگام ساخت رکورد جدید
            instance = Budgeting.objects.create(user=user,
                category=vd['category'],
                minimum_target_amount=vd['minimum_target_amount'],
                maximum_target_amount=vd['maximum_target_amount'],
                start_date=vd['start_date'], end_date=['end_date'])
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس هنگام ثبت بودجه '})
        return instance

    def update(self, instance, validated_data):
        validated_data.pop('user', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value )
        try:
            instance.save()
        except IntegrityError:
            raise serializers.ValidationError({'detail': 'خطای دیتابیس هنگام ثبت بودجه '})
        return instance




