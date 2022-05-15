from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from httpcore import request
from satellit.forms import (
    SatListForm,
    logit,
    satellit,
    ProviderListForm,
    lgt_prov,
    provider,
    FeedbackForm,
)
from satellit.function import create_xml, create_provider_xml
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
import time


# Create your views here.


def create_sat(request):
    request.session["id"] = time.asctime()
    context = dict()
    form = SatListForm(request.POST or None)

    context["form"] = form
    context["spinner"] = None

    if request.POST:

        if form.is_valid():
            # global USER_ID
            # USER_ID = request.session.get("USER_ID", time.asctime())
            # print(USER_ID)
            temp = form.cleaned_data.get("satellit")

            context["sat_xml"] = create_xml(
                temp, logit, satellit, request.session["id"]
            )
            context["data"] = " ,".join(
                f"{logit[int(i)]}|{satellit[int(i)][:-5]}" for i in temp
            )
            return render(request, "satellit/createsat.html", context)

    return render(request, "satellit/satlist.html", context)


def create_provider(request):
    request.session["id"] = time.asctime()
    context = dict()
    form = ProviderListForm(request.POST or None)
    context["form"] = form
    if request.POST:
        if form.is_valid():
            temp = form.cleaned_data.get("provider")

            context["provider_xml"] = create_provider_xml(
                temp, lgt_prov, provider, request.session["id"]  # USER_ID
            )
            context["temp"] = temp
            context["data"] = ",".join(provider[int(i)][:-5] for i in temp)
            return render(request, "satellit/createprovider.html", context)
    return render(request, "satellit/providerlist.html", context)


def get_sat_xml(request):
    return FileResponse(open(f"media/{request.session['id']}/satellites.xml", "rb"))


def contact_view(request):

    if request.method == "GET":
        form_message = FeedbackForm()
    elif request.method == "POST":

        form_message = FeedbackForm(request.POST)
        if form_message.is_valid():
            subject = request.POST.get("subject", "Create satellite")
            from_email = form_message.cleaned_data["from_email"]
            message = form_message.cleaned_data["message"]
            try:
                send_mail(
                    f"{subject} от {from_email}",
                    message,
                    from_email,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except BadHeaderError as e:
                return HttpResponse(str(e))
            return HttpResponse(
                "Mail successfully sent"
            )  # redirect("/send_email/suss")
    else:
        return HttpResponse("Не верный запрос.")
    return render(request, "satellit/home.html", {"form_message": form_message})
