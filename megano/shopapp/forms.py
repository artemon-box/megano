from django import forms


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, required=True)


class ProductReviewForm(forms.Form):
    review_text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Отзыв'}))
