from cProfile import label
import email
from email import message
from tempfile import template
from django import forms
from .function import download_sat, download_provider
from captcha.fields import CaptchaField

logit, satellit = download_sat()
lgt_prov, provider = download_provider()
sat_list = [(i, f"{logit[i]}|{satellit[i][:-5]}") for i in range(len(satellit))]
provider_list = [(i, f"{lgt_prov[i]}|{provider[i][:-4]}") for i in range(len(provider))]


class SatListForm(forms.Form):
    satellit = forms.MultipleChoiceField(
        choices=sat_list,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="choose satellite ",
    )
    captcha = CaptchaField()


class ProviderListForm(forms.Form):
    provider = forms.MultipleChoiceField(
        choices=provider_list,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="choose pvider",
    )
    captcha = CaptchaField()


class FeedbackForm(forms.Form):
    from_email = forms.EmailField(label="Email", required=True)
    message = forms.CharField(
        widget=forms.Textarea,
    )
