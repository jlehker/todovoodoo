import datetime
import json
import os
import uuid
from calendar import day_name
from decimal import Decimal

from autoslug import AutoSlugField
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, MONTHLY, WEEKLY, YEARLY, rrule, weekday
from django.contrib.postgres import fields
from django.db import models
from django.forms import model_to_dict
from django.urls import reverse
from django.utils.timezone import localdate, now
from django_slugify_processor.text import slugify
from model_utils import Choices
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField

from todovoodoo.users.models import User


class ListItem(TimeStampedModel):
    todo_list = models.ForeignKey("TodoList", on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    always_show = models.BooleanField(default=False)

    pub_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    def postpone(self, days: int = 0):
        self.due_date = localdate(now()) + relativedelta(days=days)
        self.save(update_fields=["due_date"])

    def mark_complete(self):
        self.due_date = self._next_due_date
        self.always_show = False
        self.save(update_fields=["due_date", "always_show"])

    @property
    def _next_due_date(self) -> datetime.date:
        """ Calculates the next time item will appear in master list. """
        due_date, *_ = rrule(
            freq=self.todo_list.frequency,
            interval=self.todo_list.interval,
            count=1,
            dtstart=self.due_date + relativedelta(days=1),
            byweekday=(*[weekday(i) for i in self.todo_list.weekdays],),
        )
        return due_date.date()


class TodoList(TimeStampedModel):
    FREQUENCY = Choices(
        (DAILY, "daily", "Daily"),
        (WEEKLY, "weekly", "Weekly"),
        (MONTHLY, "monthly", "Monthly"),
        (YEARLY, "yearly", "Yearly"),
    )
    INTERVAL = [(i, i) for i in range(600)]
    WEEKDAYS = Choices(*[(num, name.lower(), name) for num, name in enumerate(day_name)])

    frequency = models.PositiveSmallIntegerField(choices=FREQUENCY, default=FREQUENCY.weekly)
    interval = models.PositiveSmallIntegerField(choices=INTERVAL, default=1)
    weekdays = fields.ArrayField(
        models.PositiveSmallIntegerField(default=WEEKDAYS.monday), size=8, default=list
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField()

    pub_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    class Meta:
        unique_together = ("owner", "name")

    def add_todo(self, description: str, due_date: datetime.date) -> ListItem:
        return ListItem.objects.create(todo_list=self, description=description, due_date=due_date)

    @property
    def as_json(self) -> str:
        return json.dumps(model_to_dict(self))


# --------


class Station(TimeStampedModel):
    """
    Stations like "towel rack" or "dish washing station" that are defined by the administrator.
    """

    STATION_TYPES = Choices(("standard", "Standard"), ("checkin", "Check-In/Check-Out"))

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_id = models.UUIDField(
        unique=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Publicly viewable station identifier.",
    )
    name = models.TextField(
        blank=False,
        default="New Station",
        help_text="Name of the station. (e.g.'Towel Station', 'Bathroom')",
    )
    slug = AutoSlugField(always_update=True, populate_from="name", slugify=slugify, unique=True)
    description = models.TextField(
        blank=True,
        help_text="Description of what to include in a report entry. (e.g. 'take a picture of the towels')'",
    )
    refund_value = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal("0"))
    station_type = models.TextField(
        null=True, choices=STATION_TYPES, default=STATION_TYPES.standard
    )

    class Meta:
        unique_together = ("owner", "name")

    def get_absolute_url(self):
        return reverse("stations-public-view", args=[self.slug])


class StationItem(TimeStampedModel):
    """
    Individual item descriptions for a station.
    """

    ITEM_TYPES = Choices(("text", "Text"), ("boolean", "Boolean"), ("number", "Number"))

    station = models.ForeignKey("Station", on_delete=models.CASCADE)
    pub_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    description = models.TextField(
        blank=True,
        help_text="Description of what to include in a report entry. (e.g. 'take a picture of the towels')'",
    )
    item_type = models.TextField(null=True, choices=ITEM_TYPES, default=ITEM_TYPES.text)


def get_file_path(instance, filename):
    ext = filename.split(".")[-1]
    today = localdate(now())
    return f"photos/user_uploads/{today.year}/{today.month}/{today.day}/{uuid.uuid4()}.{ext}"


class ReportEntry(TimeStampedModel):
    """
    A guest user report entry.
    """

    REPORT_TYPES = Choices(("checkout", "Check-Out"), ("checkin", "Check-In"), ("other", "Other"))

    station = models.ForeignKey("Station", null=True, on_delete=models.SET_NULL)
    description = models.TextField(
        blank=True, help_text="Description of the state of the current state of the station."
    )
    photo_upload = models.ImageField(
        null=True, upload_to=get_file_path, help_text="Photo taken of the station."
    )
    phone_number = PhoneNumberField(blank=True, help_text="Reporter's phone number.")
    report_type = models.TextField(null=True, choices=REPORT_TYPES, default=REPORT_TYPES.other)

    def set_report_type(self):
        if self.station and self.station.station_type == Station.STATION_TYPES.checkin:
            last_entry = ReportEntry.objects.filter(
                station=self.station, phone_number=self.phone_number
            ).last()
            if last_entry and last_entry.report_type == self.REPORT_TYPES.checkin:
                self.report_type = self.REPORT_TYPES.checkout
            else:
                self.report_type = self.REPORT_TYPES.checkin


class ReportEntryItem(TimeStampedModel):
    instructions = models.TextField(blank=True)
    report_entry = models.ForeignKey(
        "ReportEntry", on_delete=models.CASCADE, related_name="%(class)s_items"
    )

    class Meta:
        abstract = True


class ReportEntryText(ReportEntryItem):
    data = models.TextField(null=False)


class ReportEntryBoolean(ReportEntryItem):
    data = models.BooleanField()


class ReportEntryNumber(ReportEntryItem):
    data = models.IntegerField()
