# -*- coding: utf-8 -*-
from selectable.base import ModelLookup
from selectable.registry import registry

from models import ActivityDetail


class ActivityLookup(ModelLookup):
    model = ActivityDetail
    search_fields = ('speaker_self', )

registry.register(ActivityLookup)