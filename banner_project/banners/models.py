# banners/models.py
from django.db import models
from django.conf import settings
import random
from ckeditor.fields import RichTextField
from django.utils.timezone import now


class Language(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='tag',
                              null=True,
                              blank=True)

    def __str__(self):
        return self.name


class Vertical(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tags = models.ManyToManyField(Tag, related_name='verticals')

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    content_url = models.URLField()  # Ссылка на index.html
    slug = models.SlugField(unique=True)  # Уникальный путь для статьи
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    verticals = models.ManyToManyField(Vertical, related_name='articles', blank=True)  # Связь с вертикалями
    random_tag_probability = models.IntegerField(default=0)  # Частота отображения рандомных баннеров от 0 до 10
    clicks = models.IntegerField(default=0)


    def __str__(self):
        return self.title

    def increment_clicks(self):
        self.clicks += 1
        self.save()


class WrittenArticle(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    content = RichTextField()
    tags = models.ManyToManyField(Tag, related_name='written_articles', blank=True)
    random_tag_probability = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, related_name='articles')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='written_article',
                              null=True,
                              blank=True)

    def __str__(self):
        return self.title


class Banner(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    link_url = models.URLField()  # Ссылка на внешний сайт при клике на баннер

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    clicks = models.IntegerField(default=0)  # Счетчик кликов
    views = models.IntegerField(default=0)  # Счетчик просмотров
    tags = models.ManyToManyField(Tag, related_name='banners', blank=True)
    verticals = models.ManyToManyField(Vertical, related_name='banners', blank=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='banner',
                              null=True,
                              blank=True)
    def __str__(self):
        return self.title

    def increment_clicks(self):
        self.clicks += 1
        self.save()

    def increment_views(self):
        self.views += 1
        self.save()

    def get_random_image(self):
        images = self.images.all()
        return random.choice(images) if images else None

    def get_best_or_random_title(self):
        titles = self.titles.all()
        if not titles:
            return None
        if all(t.clicks < 15 for t in titles):  # мало просмотров — рандом
            return random.choice(titles)
        return max(titles, key=lambda t: t.ctr())  # лучший по ctr

    def get_title_for_language(self, language):
        titles = self.titles.filter(language=language)
        if titles.exists():
            if all(t.clicks < 15 for t in titles):
                return random.choice(titles)
            return max(titles, key=lambda t: t.ctr())
        return self.get_best_or_random_title()

    def get_best_or_random_image(self):
        images = self.images.all()
        if not images:
            return None
        if all(i.clicks < 15 for i in images):
            return random.choice(images)
        return max(images, key=lambda i: i.ctr())


    @classmethod
    def create_banner(cls, title="test", description="Описание баннера", link_url="https://example.com"):
        banner = cls.objects.create(
            title=title,
            description=description,
            link_url=link_url,
            created_at=now(),
            updated_at=now(),
        )
        return banner


class BannerTitle(models.Model):
    banner = models.ForeignKey(Banner, related_name='titles', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    language = models.ForeignKey(Language, on_delete=models.CASCADE, null=True, related_name='banner_titles')
    clicks = models.IntegerField(default=0)
    views = models.IntegerField(default=0)

    def ctr(self):
        return self.clicks / self.views if self.views > 0 else 0

    def increment_clicks(self):
        self.clicks += 1
        self.save()

    def increment_views(self):
        self.views += 1
        self.save()

    def __str__(self):
        return f"Title for {self.banner.title}: {self.text}"


class BannerImage(models.Model):
    banner = models.ForeignKey(Banner, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='banner_images/', blank=True, null=True)
    clicks = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def ctr(self):
        return self.clicks / self.views if self.views > 0 else 0

    def increment_clicks(self):
        self.clicks += 1
        self.save()

    def increment_views(self):
        self.views += 1
        self.save()

    def __str__(self):
        return f"Image for {self.banner.title}"