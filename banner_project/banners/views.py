from django.shortcuts import render
from django.http import JsonResponse
from .models import Article, Banner, BannerImage, BannerTitle, Vertical, Tag, WrittenArticle
from django.shortcuts import redirect, get_object_or_404
import random
from django.utils.safestring import mark_safe


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



def written_article_with_banners(request, slug):
    article = get_object_or_404(WrittenArticle, slug=slug)
    article_tags = set(article.tags.all())

    # Собираем баннеры
    matched_banners = list(Banner.objects.filter(tags__in=article_tags).distinct())
    random_banners = list(Banner.objects.exclude(tags__in=article_tags))

    randomness_ratio = article.random_tag_probability / 10

    # Миксуем баннеры по вероятности
    final_banners = []

    while matched_banners or random_banners:
        if random.random() < randomness_ratio and random_banners:
            final_banners.append(random_banners.pop(0))
        elif matched_banners:
            final_banners.append(matched_banners.pop(0))
        else:
            break

    # Разбираем контент
    content = article.content
    slot_counter = 1
    banners_used = []

    timers = request.session.get('banner_timers', {})

    # Для каждого баннера проставляем minutes из сессии или генерим новый
    for banner in final_banners:
        key = str(banner.id)
        if key not in timers:
            timers[key] = random.randint(10, 59)
        banner.random_minutes = timers[key]

    while f"[BANNER_SLOT_{slot_counter}]" in content and final_banners:
        banner = final_banners.pop(0)
        banners_used.append(banner)

        image = banner.get_best_or_random_image()
        title = banner.get_best_or_random_title()

        banner.increment_views()
        if image:
            image.increment_views()
        if title:
            title.increment_views()

        banner_html = f"""
            <div class="banner-slot-in-text">
                <a class="banner-slot-in-text_a" href="/go/?banner_id={banner.id}&banner_title_id={title.id if title else ''}&banner_image_id={image.id if image else ''}">
                    <div class="banner-slot-in-text_img_wrapper">
                        <img src="{image.image.url if image else ''}" alt="{banner.title}">
                    </div>
                    <div class="banner-text-block">
                        <span class="banner-text-block_span">{title.text if title else banner.title}</span>
                        <span class="banner-slot_timer">{banner.random_minutes} минут назад</span>
                    </div>
                </a>
            </div>
        """
        content = content.replace(f"[BANNER_SLOT_{slot_counter}]", banner_html, 1)
        slot_counter += 1

    # Остаток баннеров — под статьёй
    remaining_banners = []

    for banner in final_banners:
        image = banner.get_best_or_random_image()
        title = banner.get_best_or_random_title()

        banner.increment_views()
        if image:
            image.increment_views()
        if title:
            title.increment_views()

        remaining_banners.append({
            'banner': banner,
            'image': image,
            'title': title,
            'ad_link': f"/go/?banner_id={banner.id}&banner_title_id={title.id if title else ''}&banner_image_id={image.id if image else ''}",
            'minutes': banner.random_minutes
        })

    request.session['banner_timers'] = timers

    return render(request, 'banners/written_article_with_banners.html', {
        'article': article,
        'content': mark_safe(content),
        'remaining_banners': remaining_banners
    })