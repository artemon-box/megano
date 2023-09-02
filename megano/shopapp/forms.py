from django import forms


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, required=True)


class AddReviewForm(forms.Form):
    review = forms.CharField()
