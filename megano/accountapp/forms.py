from django import forms


class RegistrationForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'user-input'}))
    login = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'user-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'user-input'}))

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 8:  # Пример минимальной длины имени
            self.add_error('name', "Должно содержать не менее 8 символов.")
        return name

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:  # Пример минимальной длины пароля
            self.add_error('password', "Пароль должен содержать не менее 8 символов.")
        return password