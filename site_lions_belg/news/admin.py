from django.contrib import admin
from .models import CategoryNews, TagNews, New

# Register your models here.


class CategoryNewsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CategoryNews._meta.fields]  # вывести все поля

    class Meta:
        model = CategoryNews


class TagNewsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TagNews._meta.fields]  # вывести все поля

    class Meta:
        model = TagNews


class NewAdmin(admin.ModelAdmin):
    class Meta:
        model = New

    list_display = [field.name for field in New._meta.fields]  # вывести все поля
    list_display.append('tags')
    readonly_fields = ('author',)
    list_display_links = ('title',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def tags(self, obj):
        tags = set()
        new = New.objects.get(id=obj.id)
        for tag in new.tag.all():
            tags.add(tag.name)
        if len(tags) == 0:
            return '-'
        tags = str(tags).strip("{").strip("}").replace('\'', '')
        print(" #POINT 450 - tags self: {0}".format(self))
        print(" #POINT 450.1 - tags obj: {0}".format(obj.id))
        return tags
    tags.short_description = 'Тэги'



admin.site.register(CategoryNews, CategoryNewsAdmin)
admin.site.register(TagNews, TagNewsAdmin)
admin.site.register(New, NewAdmin)
