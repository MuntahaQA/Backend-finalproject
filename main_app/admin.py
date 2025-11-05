from django.contrib import admin
from .models import Charity, Beneficiary, Program, Event, EventRegistration, ProgramApplication


admin.site.register(Charity)
admin.site.register(Beneficiary)
admin.site.register(Event)
admin.site.register(Program)
admin.site.register(EventRegistration)
admin.site.register(ProgramApplication)