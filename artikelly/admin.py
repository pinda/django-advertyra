from django.contrib import admin

from artikelly.models import Article

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status')
    list_filter = ('status', )

admin.site.register(Article, ArticleAdmin)
