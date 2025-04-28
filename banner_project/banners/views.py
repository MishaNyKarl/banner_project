from django.shortcuts import render
from django.http import JsonResponse
from .models import Article, Banner, BannerImage, BannerTitle, Vertical, Tag
from django.shortcuts import redirect, get_object_or_404
import random


def banner_redirect(request):
    banner_id = request.GET.get('banner_id')
    title_id = request.GET.get('banner_title_id')
    image_id = request.GET.get('banner_image_id')

    if banner_id:
        get_object_or_404(Banner, id=banner_id).increment_clicks()
    if title_id:
        get_object_or_404(BannerTitle, id=title_id).increment_clicks()
    if image_id:
        get_object_or_404(BannerImage, id=image_id).increment_clicks()

    banner = get_object_or_404(Banner, id=banner_id)
    return redirect(banner.link_url)


def get_tags_by_verticals(request):
    # Получаем список выбранных вертикалей
    vertical_ids = request.GET.getlist('verticals')

    # Получаем все теги, связанные с выбранными вертикалями
    tags = Tag.objects.filter(verticals__id__in=vertical_ids).distinct()

    # Возвращаем выбранные теги в JSON формате
    selected_tags = [tag.id for tag in tags]
    return JsonResponse({'selected_tags': selected_tags})


def article_with_banners(request, slug):
    article = get_object_or_404(Article, slug=slug)
    article_tags = set(article.tags.all())

    # Группируем баннеры
    matched_banners = []
    random_banners = []

    for banner in Banner.objects.all():
        banner_tags = set(banner.tags.all())
        if banner_tags & article_tags:
            matched_banners.append(banner)
        else:
            random_banners.append(banner)

    # Контроль рандомности
    randomness_ratio = article.random_tag_probability / 10

    final_banners = list(matched_banners)

    # Добавляем случайные баннеры по вероятности
    for banner in random_banners:
        if random.random() < randomness_ratio:
            final_banners.append(banner)

    # Убираем дубли (если вдруг)
    final_banners = list(set(final_banners))

    # Перемешиваем порядок
    random.shuffle(final_banners)

    # Готовим к отображению
    banners_with_variants = []
    for banner in final_banners:
        image = banner.get_best_or_random_image()
        title = banner.get_best_or_random_title()

        banner.increment_views()
        if image:
            image.increment_views()
        if title:
            title.increment_views()

        banners_with_variants.append({
            'banner': banner,
            'image': image,
            'title': title,
            'ad_link': f"/go/?banner_id={banner.id}&banner_title_id={title.id if title else ''}&banner_image_id={image.id if image else ''}"
        })

    if request.GET.get('banner_title_id'):
        title = get_object_or_404(BannerTitle, id=request.GET['banner_title_id'])
        title.increment_clicks()

    if request.GET.get('banner_image_id'):
        image = get_object_or_404(BannerImage, id=request.GET['banner_image_id'])
        image.increment_clicks()

    if request.GET.get('banner_id'):
        banner = get_object_or_404(Banner, id=request.GET['banner_id'])
        banner.increment_clicks()

    print(matched_banners, random_banners)
    print(final_banners)
    return render(request, 'banners/article_with_banners.html', {
        'article': article,
        'banners': banners_with_variants,
    })