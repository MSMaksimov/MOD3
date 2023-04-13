from django import forms
from django.core import validators
from django.forms import ModelForm
from django.contrib.auth.models import Group

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount"


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["name"]
