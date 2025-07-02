from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as DefaultGroupAdmin
from django.forms import ModelForm
from .models import (
    Banner, Article, BannerImage, BannerTitle,
    Tag, WrittenArticle, Language
)
from django.utils.timezone import now

User = get_user_model()


# ------------------------------------------------
# 1) Общий класс для «владельческих» моделей
# ------------------------------------------------
class OwnedAdmin(admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        # если суперпользователь — не исключаем ничего (покажем все поля, включая owner)
        if request.user.is_superuser:
            return ()
        # иначе — убираем owner
        return ('owner',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # только те, что принадлежат пользователю
        return qs.filter(owner=request.user)

        # при сохранении: если юзер не супер — owner назначаем автоматически
    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not change:
            obj.owner = request.user
        obj.save()


# ------------------------------------------------
# 2) Переопределяем UserAdmin, скрывая пользователей от staff
# ------------------------------------------------
class UserAdmin(DefaultUserAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# Группы тоже прячем от всех, кроме superuser
admin.site.unregister(Group)


# Регистрируем заново с нашим контролем прав
@admin.register(Group)
class GroupAdmin(DefaultGroupAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ------------------------------------------------
# 3) Inline для Banner
# ------------------------------------------------
class BannerImageInline(admin.TabularInline):
    model = BannerImage
    extra = 1


class BannerTitleInline(admin.TabularInline):
    model = BannerTitle
    extra = 1


# ------------------------------------------------
# 4) Админка для Banner с владельческим поведением
# ------------------------------------------------
@admin.register(Banner)
class BannerAdmin(OwnedAdmin):
    inlines = [BannerTitleInline, BannerImageInline]
    list_display = ('title', 'description', 'get_tags', 'owner')
    filter_horizontal = ('tags',)  # Добавляем возможность выбора нескольких тегов и вертикалей
    actions = ['create_sample_banner']

    def get_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    get_tags.short_description = 'Tags'


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


# ------------------------------------------------
# 5) Админка для Article
# ------------------------------------------------
class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'description', 'slug', 'content_url',
                  'tags', 'random_tag_probability']



@admin.register(Article)
class ArticleAdmin(OwnedAdmin):
    form = ArticleForm
    list_display = ('title', 'description', 'get_tags')
    search_fields = ('title', 'description')
    filter_horizontal = ('tags', )


    def get_tags(self, obj):
        return ", ".join(t.name for t in obj.tags.all())
    get_tags.short_description = 'Tags'


# ------------------------------------------------
# 6) Админка для WrittenArticle
# ------------------------------------------------
class WrittenArticleForm(ModelForm):
    class Meta:
        model = WrittenArticle
        fields = ['title', 'language', 'description', 'slug', 'content', 'tags', 'owner']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tags'].queryset = Tag.objects.all()


@admin.register(WrittenArticle)
class WrittenArticleAdmin(OwnedAdmin):
    form = WrittenArticleForm
    list_display = ('title', 'slug', 'created_at', 'owner')
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('tags',)


# ------------------------------------------------
# 7) Простые модели без owner-фильтрации
# ------------------------------------------------
@admin.register(Tag)
class TagAdmin(OwnedAdmin):
    pass


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass
