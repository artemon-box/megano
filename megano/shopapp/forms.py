from django import forms
import json
from django.forms import Media, widgets

from shopapp.models import ProductFeature, Feature, FeatureValue


class AddToCartForm(forms.Form):
    order_quantity = forms.IntegerField(min_value=0, required=True)


class ProductReviewForm(forms.Form):
    review_text = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Отзыв'}))


class RestrictedSelect(widgets.Select):
    @property
    def media(self):
        media = super().media
        media += Media(js=["assets/js/restricted-model-choice-field.js"])
        return media


class BoundRestrictedModelChoiceField(forms.BoundField):
    def get_restrictions(self):
        restrictions = {}

        restrict_on_form_field = self.form.fields[self.field.restrict_on_form_field]
        # Можно оптимизировать
        for restricting_object in restrict_on_form_field.queryset:
            allowed_objects = self.field.queryset.filter(**{self.field.restrict_on_relation: restricting_object})
            for obj in allowed_objects:
                restrictions.setdefault(obj.id, set()).add(restricting_object.id)

        return restrictions

    def build_widget_attrs(self, attrs, widget=None):
        attrs = super().build_widget_attrs(attrs, widget)

        restrictions = self.get_restrictions()
        restrictions = {k: [str(v) for v in vs] for k, vs in restrictions.items()}
        attrs["data-restrictions"] = json.dumps(restrictions)

        bound_restrict_on_form_field = self.form[self.field.restrict_on_form_field]
        attrs["data-restricted-on"] = bound_restrict_on_form_field.html_name

        return attrs


class RestrictedModelChoiceField(forms.ModelChoiceField):
    widget = RestrictedSelect

    def __init__(self, *args, restrict_on_form_field: str = None, restrict_on_relation: str = None, **kwargs):
        super().__init__(*args, **kwargs)

        if not restrict_on_form_field:
            raise ValueError("restrict_on_form_field is required")
        self.restrict_on_form_field = restrict_on_form_field

        if not restrict_on_relation:
            raise ValueError("restrict_on_relation is required")
        self.restrict_on_relation = restrict_on_relation

    def get_bound_field(self, form, field_name):
        return BoundRestrictedModelChoiceField(form, self, field_name)


class ProductFeatureForm(forms.ModelForm):
    class Meta:
        model = ProductFeature
        fields = "__all__"

    feature = RestrictedModelChoiceField(
        Feature.objects.all(),
        restrict_on_form_field="category",
        restrict_on_relation="allowedrelation__category",
    )
    value = RestrictedModelChoiceField(
        FeatureValue.objects.all(),
        restrict_on_form_field="feature",
        restrict_on_relation="allowedrelation__feature",
    )


class FileImportForm(forms.Form):
    file = forms.FileField()
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'введите почту для отправки уведомления',
                'size': 40,
            }
        )
    )
