# banners/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from banners.models import (
    Language, Tag,
    Banner, BannerTitle, BannerImage,
    WrittenArticle
)

User = get_user_model()

class LanguageModelTest(TestCase):
    def test_str(self):
        lang = Language.objects.create(code='ru', name='Russian')
        self.assertEqual(str(lang), 'Russian')


class BannerTitleAndImageTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass')
        self.banner = Banner.objects.create(
            title='Test', description='Desc', link_url='http://x', owner=self.user
        )
        # Один title с просмотрами и кликами
        self.title = BannerTitle.objects.create(
            banner=self.banner, text='Hello', language=None, clicks=3, views=6
        )
        # Один image с просмотрами и кликами
        self.image = BannerImage.objects.create(
            banner=self.banner, image='i.png', clicks=2, views=4
        )

    def test_ctr_and_increment(self):
        # BannerTitle.ctr
        self.assertAlmostEqual(self.title.ctr(), 3/6)
        self.title.increment_clicks()
        self.title.increment_views()
        self.title.refresh_from_db()
        self.assertEqual((self.title.clicks, self.title.views), (4, 7))

        # BannerImage.ctr
        self.assertAlmostEqual(self.image.ctr(), 2/4)
        self.image.increment_clicks()
        self.image.increment_views()
        self.image.refresh_from_db()
        self.assertEqual((self.image.clicks, self.image.views), (3, 5))


class BannerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bob', password='pw')
        self.banner = Banner.objects.create(
            title='B', description='', link_url='#', owner=self.user
        )
        # добавим три title: два без language, один с
        BannerTitle.objects.create(banner=self.banner, text='T1', language=None, clicks=0, views=0)
        BannerTitle.objects.create(banner=self.banner, text='T2', language=None, clicks=20, views=20)
        # title на другом языке
        self.lang = Language.objects.create(code='en', name='English')
        BannerTitle.objects.create(banner=self.banner, text='T_en', language=self.lang, clicks=5, views=10)

        # картинки
        BannerImage.objects.create(banner=self.banner, image='a.png', clicks=1, views=2)
        BannerImage.objects.create(banner=self.banner, image='b.png', clicks=0, views=0)

    def test_get_random_image(self):
        # точнее – вернёт либо первую, либо вторую
        img = self.banner.get_random_image()
        self.assertIn(img, list(self.banner.images.all()))

    def test_get_best_or_random_title(self):
        # поскольку есть title с clicks=20, views=20 → ctr=1, это лучший
        best = self.banner.get_best_or_random_title()
        self.assertEqual(best.text, 'T2')

    def test_get_best_or_random_image(self):
        # первая картинка имеет ctr=0.5, вторая — ctr=0
        best_img = self.banner.get_best_or_random_image()
        self.assertEqual(best_img.clicks, 1)

    def test_get_title_for_language(self):
        ru_lang = Language.objects.create(code='ru', name='Russian')
        t_ru = self.banner.get_title_for_language(ru_lang)
        self.assertEqual(t_ru.text, 'T2')

        # при запросе en найдётся один → вернуть его
        t_en = self.banner.get_title_for_language(self.lang)
        self.assertEqual(t_en.text, 'T_en')


class WrittenArticleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('kate', password='pw')
        self.lang = Language.objects.create(code='ru', name='Russian')
        self.w = WrittenArticle.objects.create(
            title='WA', description='D', slug='wa-slug',
            content='<p>Hi</p>', language=self.lang,
            random_tag_probability=3, owner=self.user
        )

    def test_str_and_fields(self):
        self.assertEqual(str(self.w), 'WA')
        self.assertEqual(self.w.language, self.lang)
        self.assertEqual(self.w.owner, self.user)

    def test_owner_and_language_nullable(self):
        # можно создать без owner/language?
        wa2 = WrittenArticle.objects.create(
            title='X', description='', slug='x', content='c',
            random_tag_probability=0
        )
        self.assertIsNone(wa2.owner)
        self.assertIsNone(wa2.language)
