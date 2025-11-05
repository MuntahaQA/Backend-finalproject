from django.contrib import admin
from .models import Charity, Beneficiary, Program, Event, EventRegistration, ProgramApplication


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'ministry_owner', 'estimated_beneficiaries', 'status', 'created_at']
    list_filter = ['status', 'ministry_owner', 'created_at']
    search_fields = ['name', 'ministry_owner', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'ministry_owner', 'status')
        }),
        ('Beneficiaries', {
            'fields': ('estimated_beneficiaries', 'max_capacity')
        }),
        ('Eligibility & Dates', {
            'fields': ('eligibility_criteria', 'start_date', 'end_date', 'application_deadline')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Charity)
admin.site.register(Beneficiary)
admin.site.register(Event)
admin.site.register(EventRegistration)
admin.site.register(ProgramApplication)