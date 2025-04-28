from django.forms import ModelForm
from django.contrib import admin
from .models import Banner, Article, BannerImage, BannerTitle, Tag, Vertical
from django.utils.safestring import mark_safe


class BannerImageInline(admin.TabularInline):
    model = BannerImage
    extra = 1


class BannerTitleInline(admin.TabularInline):
    model = BannerTitle
    extra = 1


class BannerAdmin(admin.ModelAdmin):
    inlines = [BannerTitleInline, BannerImageInline]
    list_display = ('title', 'description', 'get_tags', 'get_verticals')
    # search_fields = ('title', 'description')
    filter_horizontal = ('tags', 'verticals')  # Добавляем возможность выбора нескольких тегов и вертикалей

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def get_verticals(self, obj):
        return ", ".join([vertical.name for vertical in obj.verticals.all()])
    get_verticals.short_description = 'Verticals'


class VerticalAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_tags')
    search_fields = ('name',)
    filter_horizontal = ('tags',)  # Удобный выбор тегов для вертикали

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])

    get_tags.short_description = 'Tags'


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'description', 'slug','content_url', 'tags', 'verticals', 'random_tag_probability']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # Если это уже существующая статья
            verticals = self.instance.verticals.all()
            tags = Tag.objects.filter(verticals__in=verticals).distinct()
            self.fields['tags'].initial = tags


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleForm
    list_display = ('title', 'description', 'get_verticals', 'get_tags')
    search_fields = ('title', 'description')
    filter_horizontal = ('verticals', 'tags')  # Удобный выбор нескольких тегов и вертикалей

    def get_verticals(self, obj):
        return ", ".join([vertical.name for vertical in obj.verticals.all()])
    get_verticals.short_description = 'Verticals'

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'




admin.site.register(Article, ArticleAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Tag)
admin.site.register(Vertical, VerticalAdmin)

