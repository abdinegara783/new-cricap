from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Response, RESPONSE_CHOICES
from .models import DataDiri

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Form untuk mengumpulkan jawaban responden
class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['response']
        widgets = {
            'response': forms.RadioSelect(choices=RESPONSE_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        # Menambahkan pertanyaan ke form untuk identifikasi
        self.question = kwargs.pop('question', None)
        super().__init__(*args, **kwargs)  


class DataDiriForm(forms.ModelForm):
    class Meta:
        model = DataDiri
        fields = [
            'nama', 'usia', 'jenis_kelamin', 'status_perkawinan',
            'pendidikan', 'tempat_tinggal', 'kabupaten_kota', 'pekerjaan'
        ]
        widgets = {
            'jenis_kelamin': forms.RadioSelect,
            'status_perkawinan': forms.RadioSelect,
        }
