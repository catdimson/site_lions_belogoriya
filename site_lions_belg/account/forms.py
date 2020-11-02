from django import forms
from .models import Sportsman


class SportsmanForm(forms.ModelForm):
    class Meta:
        model = Sportsman
        fields = ['age', 'phone', 'photo']

        widgets = {
            'photo': forms.FileInput(),             # убралась абракадабра (ссылка, лишний текст и тд)
        }

    def __init__(self, *args, **kwargs):
        super(SportsmanForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'photo':
                field.widget.attrs['class'] = 'form-control-file'
            else:
                field.widget.attrs['class'] = 'form-control'
        self.fields['photo'].label = "Фотография"
        self.fields['phone'].label = "Телефон"
        self.fields['age'].label = "Возраст"

