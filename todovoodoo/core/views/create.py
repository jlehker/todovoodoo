from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.timezone import now, localdate
from django.views.generic import DeleteView, CreateView, TemplateView, UpdateView

from todovoodoo.core.forms import (
    ListItemForm,
    TodoListForm,
    StationForm,
    StationItemForm,
    ReportEntryForm,
)
from todovoodoo.core.models import ListItem, TodoList, Station, StationItem, ReportEntry


class ReportEntryCreateView(CreateView):

    slug_url_kwarg = "slug"
    slug_field = "slug"
    form_class = ReportEntryForm
    model = ReportEntry

    def get_context_data(self, *args, **kwargs):
        """Use this to add extra context."""
        context = super().get_context_data(**kwargs)

        slug = self.kwargs.get("slug")
        if not slug:
            return context

        try:
            station = Station.objects.get(slug=slug)
        except Station.DoesNotExist:
            return redirect(reverse("core:stations-public-view"))
        else:
            context.update({"slug": slug, "station": station})

        return context

    def get_success_url(self):
        return reverse("core:stations-public-view")

    def form_valid(self, form):
        slug = self.kwargs["slug"]
        try:
            station = Station.objects.get(slug=slug)
        except Station.DoesNotExist:
            return redirect(reverse("core:stations-public-view", args=[slug]))
        form.instance.station = station
        form.save()
        return super().form_valid(form)


public_station_view = ReportEntryCreateView.as_view()


class StationView(LoginRequiredMixin, TemplateView):

    template_name = "core/station_configuration.html"

    def get_context_data(self, pub_id=None, **kwargs):
        """Use this to add extra context."""
        todo_lookup_args = {"pub_id": pub_id} if pub_id is not None else {"name": "main"}
        try:
            station = Station.objects.get(owner=self.request.user, **todo_lookup_args)
        except Station.DoesNotExist:
            return redirect(reverse("core:lists-view"))
        context = super(StationView, self).get_context_data(**kwargs)
        context.update(
            {
                "stations": Station.objects.filter(owner=self.request.user).order_by("created"),
                "list_items": station.stationitem_set.order_by("-created"),
                "active_list": station,
                "can_delete": True if station.name != "main" else False,
                "list_item_edit_form": ListItemForm(prefix="list_item_edit"),
                "list_item_create_form": ListItemForm(prefix="list_item_create"),
                "todo_list_form": StationForm(),
                "station_url": self.request.build_absolute_uri(
                    reverse("core:lists-view", args=[station.pub_id])
                ),
            }
        )
        return context


station_view = StationView.as_view()


class ListItemCreate(LoginRequiredMixin, CreateView):

    form_class = ListItemForm
    prefix = "list_item_create"
    model = ListItem

    def form_valid(self, form):
        try:
            todo_list = TodoList.objects.get(owner=self.request.user, pub_id=self.kwargs["pub_id"])
        except TodoList.DoesNotExist:
            return redirect(reverse("core:lists-view"))
        form.instance.todo_list = todo_list
        form.instance.due_date = localdate(now())
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.POST.get("next", self.success_url)


list_item_create_view = ListItemCreate.as_view()


class ListItemDelete(LoginRequiredMixin, DeleteView):

    slug_url_kwarg = "pub_id"
    slug_field = "pub_id"
    success_url = reverse_lazy("core:lists-view")

    def get_queryset(self):
        return ListItem.objects.filter(todo_list__owner=self.request.user)

    def get_success_url(self):
        return self.request.POST.get("next", self.success_url)


list_item_delete_view = ListItemDelete.as_view()


class ListItemUpdate(LoginRequiredMixin, UpdateView):

    slug_url_kwarg = "pub_id"
    slug_field = "pub_id"
    prefix = "list_item_edit"
    success_url = reverse_lazy("core:lists-view")
    fields = ["description", "always_show"]

    def get_queryset(self):
        return ListItem.objects.filter(todo_list__owner=self.request.user)

    def get_success_url(self):
        return self.request.POST.get("next", self.success_url)


list_item_update_view = ListItemUpdate.as_view()


class StationCreate(LoginRequiredMixin, CreateView):
    """ Creates a new list for items. """

    form_class = StationForm
    model = Station
    success_url = reverse_lazy("core:lists-view")

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except IntegrityError:
            messages.add_message(
                request, messages.ERROR, "All of your Station names must be unique."
            )
            return redirect(request.POST.get("next", self.success_url))

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.request.POST.get("next", self.success_url)


todo_list_create_view = StationCreate.as_view()


class TodoListUpdate(LoginRequiredMixin, UpdateView):

    slug_url_kwarg = "pub_id"
    slug_field = "pub_id"
    form_class = TodoListForm
    success_url = reverse_lazy("core:lists-view")

    def get_queryset(self):
        return TodoList.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return self.request.POST.get("next", self.success_url)


todo_list_update_view = TodoListUpdate.as_view()


class TodoListDelete(LoginRequiredMixin, DeleteView):
    """ Deletes a list. """

    slug_url_kwarg = "pub_id"
    slug_field = "pub_id"
    success_url = reverse_lazy("core:lists-view")

    def get_queryset(self):
        return TodoList.objects.filter(owner=self.request.user).exclude(name__iexact="main")


todo_list_delete_view = TodoListDelete.as_view()
