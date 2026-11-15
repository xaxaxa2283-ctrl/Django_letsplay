from django import forms


class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=200, label='Имя')
    phone = forms.CharField(max_length=20, label='Телефон')
    email = forms.EmailField(required=False, label='Email')
    delivery_method = forms.ChoiceField(choices=[('pickup', 'Самовывоз'), ('courier', 'Курьер'), ('post', 'Отправка')])
    address = forms.CharField(required=False, label='Адрес')
    payment_method = forms.ChoiceField(choices=[('cash', 'Наличные'), ('card', 'Карта')])
    comment = forms.CharField(required=False)

    def clean(self):
        data = super().clean()
        if data.get('delivery_method') in ('courier', 'post') and not data.get('address'):
            self.add_error('address', 'Укажите адрес доставки.')
        return data
