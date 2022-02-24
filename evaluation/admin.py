from django.contrib import admin
from . models import *

class Labels(admin.TabularInline):
    model = Label
    extra = 0
    fk_name = "question"

class Options(admin.TabularInline):
    model = Option
    extra = 0
    fk_name = "question"

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [Labels, Options]
admin.site.register(Question, QuestionAdmin)










class LsLabels(admin.TabularInline):
    model = Lslabel
    extra = 0
    fk_name = "logical_string"

class LogicalStringAdmin(admin.ModelAdmin):
    list_display = ('text',)
    inlines = [LsLabels]
admin.site.register(LogicalString, LogicalStringAdmin)







admin.site.register(DifinedLabel)
admin.site.register(Biofuel)
admin.site.register(Evaluator)
admin.site.register(Option)

