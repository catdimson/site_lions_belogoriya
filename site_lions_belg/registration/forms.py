from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    # переопределяем поля формы
    def __init__(self, *args,  **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields["username"].label = 'Логин'
        self.fields["password"].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с данным логином не зерагистрирован в системе')
        user = User.objects.get(username=username)
        # андартная функция check_password проверяет пароль
        if user and not user.check_password(password):
            raise forms.ValidationError('Неверный пароль')


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_check = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        # поля, которые будут отображаться
        fields = [
            'username',
            'password',
            'password_check',
            'first_name',
            'last_name',
            'email'
        ]

    # десь мы определяем как поля будут выводиться (на русском языке)
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
        self.fields['password'].help_text = 'Придумайте пароль'
        self.fields['password_check'].label = 'Повторите пароль'
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['email'].label = 'Ваша почта'
        self.fields['email'].help_text = 'Пожалуйста, указывайте реальный адрес'

    def clean(self):
        username = self.cleaned_data['username']
        passwrod = self.cleaned_data['password']
        passwrod_check = self.cleaned_data['password_check']
        email = self.cleaned_data['email']

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с данным логином уже зерагистрирован в системе')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с данным почтовым адресом уже зерагистрирован в системе')
        if passwrod != passwrod_check:
            raise forms.ValidationError('Ваши пароли не совпадают. Попробуйте снова')