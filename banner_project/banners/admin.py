from django.forms import ModelForm
from django.contrib import admin
from .models import Banner, Article, BannerImage, BannerTitle, Tag, Vertical, WrittenArticle
from django.utils.safestring import mark_safe
from django.utils.timezone import now


class BannerImageInline(admin.TabularInline):
    model = BannerImage
    extra = 1


class BannerTitleInline(admin.TabularInline):
    model = BannerTitle
    extra = 1


class BannerAdmin(admin.ModelAdmin):
    inlines = [BannerTitleInline, BannerImageInline]
    list_display = ('title', 'description', 'get_tags', 'get_verticals')
    filter_horizontal = ('tags', 'verticals')  # Добавляем возможность выбора нескольких тегов и вертикалей
    actions = ['create_sample_banner']

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'

    def get_verticals(self, obj):
        return ", ".join([vertical.name for vertical in obj.verticals.all()])
    get_verticals.short_description = 'Verticals'

    def create_sample_banner(self, request, queryset):
        title = "automatically_created_banner"
        description = "test"
        link_url = "https://example.com/viniry"
        created_at = updated_at = now()

        # Создаём баннер
        banner = Banner.objects.create(
            title=title,
            description=description,
            link_url=link_url,
            created_at=created_at,
            updated_at=updated_at
        )

        tag1 = Tag.objects.get(name='tag1')
        tag2 = Tag.objects.get(name='tag2')
        banner.tags.add(tag1, tag2)

        BannerTitle.objects.create(
            banner=banner,
            text='Пьеха: "Этот метод борьбы с диабетом, помогает мне быть на ногах сутками! Скорей запишите рецепт...'
        )

        image_path = "banner_images/1642975718_24-fonzon-club-p-igri-v-stile-3d-31.jpg"
        BannerImage.objects.create(
            banner=banner,
            image=image_path
        )

        self.message_user(request, "Баннер успешно создан!")

    create_sample_banner.short_description = "Создать пример баннера"


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


class WrittenArticleForm(ModelForm):
    class Meta:
        model = WrittenArticle
        fields = ['title', 'description', 'slug', 'content', 'tags', 'random_tag_probability']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.all()


@admin.register(WrittenArticle)
class WrittenArticleAdmin(admin.ModelAdmin):
    form = WrittenArticleForm
    list_display = ('title', 'slug', 'created_at')
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('tags',)

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'






admin.site.register(Article, ArticleAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Tag)
admin.site.register(Vertical, VerticalAdmin)

