from django.contrib import admin
from .models import MysteryShoppingOverview, MysteryShoppingDetail, MysteryShoppingImages, MysteryChecklistPersonResponsible
# Register your models here.
admin.site.register(MysteryShoppingOverview)
admin.site.register(MysteryShoppingDetail)
admin.site.register(MysteryShoppingImages)
admin.site.register(MysteryChecklistPersonResponsible)
# admin.site.register(MonthAudit)
