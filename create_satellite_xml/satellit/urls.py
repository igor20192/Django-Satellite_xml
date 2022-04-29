from re import template
from django.urls import path
from django.views.generic import TemplateView
from satellit.views import create_sat, get_sat_xml, create_provider, contact_view
from satellit.forms import FeedbackForm

form_message = FeedbackForm()
urlpatterns = [
    path(
        "",
        TemplateView.as_view(
            template_name="satellit/home.html",
            extra_context={"form_message": form_message},
        ),
        name="home",
    ),
    path("satellite_list/", create_sat, name="create_satellit"),
    path("download/", get_sat_xml, name="download"),
    path("provider_list/", create_provider, name="create_provider"),
    path("send_email/", contact_view, name="send_email"),
]
