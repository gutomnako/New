from django.forms import ModelForm
from .models import Resort


class ResortForm(ModelForm):
    class Meta:
        model = Resort
        fields = '__all__'

