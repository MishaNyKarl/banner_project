# banners/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from ..models import (
    Banner, BannerTitle, BannerImage,
    Tag, Vertical, Article, WrittenArticle, Language
)

User = get_user_model()


class ViewsTest(TestCase):
    def setUp(self):
        # клиент
        self.client = Client()

        # создаём двоих юзеров
        self.u1 = User.objects.create_user('u1', password='pw')
        self.u2 = User.objects.create_user('u2', password='pw')

        # язык
        self.lang_ru = Language.objects.create(code='ru', name='Russian')
        self.lang_en = Language.objects.create(code='en', name='English')

        # теги и вертикаль
        self.tag1 = Tag.objects.create(name='tag1', owner=self.u1)
        self.tag2 = Tag.objects.create(name='tag2', owner=self.u1)
        self.vert = Vertical.objects.create(name='vert1')
        self.vert.tags.add(self.tag1, self.tag2)

        # баннер 1 у u1, прикрепляем к тегу1
        self.banner1 = Banner.objects.create(
            title='B1', description='D1', link_url='/ok1/', owner=self.u1
        )
        BannerTitle.objects.create(banner=self.banner1, text='T1_ru', language=self.lang_ru)
        BannerTitle.objects.create(banner=self.banner1, text='T1_en', language=self.lang_en)
        BannerImage.objects.create(banner=self.banner1, image='i1.png')

        self.banner1.tags.add(self.tag1)

        # баннер 2 у u1, без общих тегов
        self.banner2 = Banner.objects.create(
            title='B2', description='D2', link_url='/ok2/', owner=self.u1
        )
        BannerTitle.objects.create(banner=self.banner2, text='T2_ru', language=self.lang_ru)
        BannerImage.objects.create(banner=self.banner2, image='i2.png')

        # статичная статья у u1 с tag1
        self.article = Article.objects.create(
            title='Art1', description='Desc', content_url='http://x', slug='art1'
        )
        self.article.tags.add(self.tag1)

        # написанная статья у u1 c одним слотом
        self.written = WrittenArticle.objects.create(
            title='WA1', description='Desc', slug='wa1',
            content='<p>before[BANNER_SLOT_1]after</p>',
            language=self.lang_ru, random_tag_probability=1, owner=self.u1
        )
        self.written.tags.add(self.tag1)

    def test_homepage(self):
        url = reverse('home_page')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        items = resp.context['banner_items']
        # должно быть len(banner.images)*len(banner.titles)
        self.assertTrue(any('image_url' in it and 'title' in it and 'ad_link' in it
                            for it in items))

    def test_banner_redirect_increments_click_and_redirects(self):
        url = reverse('banner_redirect') + f'?banner_id={self.banner1.id}'
        resp = self.client.get(url)
        self.banner1.refresh_from_db()
        self.assertEqual(self.banner1.clicks, 1)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], '/ok1/')

    def test_get_tags_by_verticals(self):
        url = reverse('get_tags_by_verticals') + f'?verticals={self.vert.id}'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn(self.tag1.id, data['selected_tags'])
        self.assertIn(self.tag2.id, data['selected_tags'])

    def test_article_with_banners_matches_and_random(self):
        url = reverse('article_with_banners', args=[self.article.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        banners = [b['banner'] for b in resp.context['banners']]
        # баннер1 имеет общий тег → должен быть в списке
        self.assertIn(self.banner1, banners)

    def test_written_article_with_banners_renders_slots_and_labels(self):
        url = reverse('written_article_with_banners', args=[self.written.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode()
        # проверяем, что слот заменён на div.banner-slot-in-text
        self.assertIn('class="banner-slot-in-text"', html)
        # проверяем метку времени и "Читайте также"
        self.assertIn('минут назад', html)
        self.assertIn('Читайте также', html)

    def test_written_article_filters_by_owner_for_banners(self):
        # переназначим владельца статьи u2, баннеры у u1 не должны попасть
        self.written.owner = self.u2
        self.written.save()
        url = reverse('written_article_with_banners', args=[self.written.slug])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # ни один баннер не должен быть у u2.owner=u2,
        # а у статьи нет тегов у баннеров u2 → список пуст
        self.assertFalse(resp.context['remaining_banners'])
