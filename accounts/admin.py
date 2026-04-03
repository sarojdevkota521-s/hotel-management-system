from django.contrib import admin
from django.contrib.admin import display

from .models import User
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)

    # @display(description="role", label={
    #     'customer': 'info',
    #     'staff': 'success',
    #     'admin': 'warning',
    # })
    # def role_badge(self, obj):
    #     return obj.role
