from django.db import models
from django.contrib import admin


class MainCategory(models.Model):
    tag = models.CharField(max_length=200)

    def __str__(self):
        return self.tag


class SubCategory(models.Model):
    main_category = models.ForeignKey('MainCategory', on_delete=models.CASCADE)
    tag = models.CharField(max_length=200)

    def __str__(self):
        return self.tag


class Collection(models.Model):
    tag = models.CharField(max_length=200)


class Keyword(models.Model):
    tag = models.CharField(max_length=200)

    def __str__(self):
        return self.tag


class MainCategoryAdmin(admin.ModelAdmin):
    fields = ['tag']

    def __str__(self):
        return self.tag


class SubCategoryAdmin(admin.ModelAdmin):
    fields = ['main_category', 'tag']


class CollectionAdmin(admin.ModelAdmin):
    fields = ['tag']

    def __str__(self):
        return self.tag


class KeywordAdmin(admin.ModelAdmin):
    fields = ['tag']


admin.site.register(MainCategory, MainCategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Keyword, KeywordAdmin)
