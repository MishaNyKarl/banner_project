# banners/tests/test_admin.py
from django.test import TestCase, RequestFactory
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from banners.models import Banner, Tag, WrittenArticle, Language
from banners.admin import BannerAdmin, OwnedAdmin, UserAdmin, GroupAdmin

User = get_user_model()


class OwnedAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = admin.AdminSite()
        # создаём пользователей
        self.superuser = User.objects.create_superuser('su', 'su@x', 'pw')
        self.staff = User.objects.create_user('st', 'st@x', 'pw', is_staff=True)
        # создаём объекты с разными владельцами
        self.b1 = Banner.objects.create(title='b1', description='', link_url='#', owner=self.staff)
        self.b2 = Banner.objects.create(title='b2', description='', link_url='#', owner=self.superuser)
        # вручную инстанцируем админ для Banner
        self.ma = BannerAdmin(Banner, self.site)

    def test_get_queryset_superuser(self):
        req = self.factory.get('/')
        req.user = self.superuser
        qs = self.ma.get_queryset(req)
        # суперпользователь видит оба баннера
        self.assertCountEqual(list(qs), [self.b1, self.b2])

    def test_get_queryset_staff(self):
        req = self.factory.get('/')
        req.user = self.staff
        qs = self.ma.get_queryset(req)
        # staff видит только свой баннер
        self.assertListEqual(list(qs), [self.b1])

    def test_get_exclude(self):
        # у staff поле owner должно быть скрыто
        req = self.factory.get('/')
        req.user = self.staff
        excl = self.ma.get_exclude(req)
        self.assertIn('owner', excl)

        # у суперпользователя ничего не исключаем
        req.user = self.superuser
        self.assertEqual(tuple(self.ma.get_exclude(req)), ())

    def test_save_model_assigns_owner_for_staff(self):
        # эмулируем создание нового объекта staff
        req = self.factory.post('/')
        req.user = self.staff
        new = Banner(title='x', description='', link_url='#')
        form = None
        self.ma.save_model(req, new, form, change=False)
        # после save_model у нового должен установиться owner=staff
        self.assertEqual(new.owner, self.staff)

    def test_save_model_superuser_keeps_owner(self):
        req = self.factory.post('/')
        req.user = self.superuser
        new = Banner(title='x2', description='', link_url='#', owner=self.staff)
        self.ma.save_model(req, new, None, change=False)
        # суперюзер не перезаписывает owner
        self.assertEqual(new.owner, self.staff)


class UserAndGroupAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = admin.AdminSite()
        self.superuser = User.objects.create_superuser('su', 'su@x', 'pw')
        self.staff = User.objects.create_user('st', 'st@x', 'pw', is_staff=True)

        # UserAdmin зарегистрирован в admin.site, но мы тестируем его методы напрямую
        self.ua = UserAdmin(User, self.site)
        self.ga = GroupAdmin(Group, self.site)

    def test_useradmin_permissions(self):
        req = self.factory.get('/')
        # для staff все методы должны вернуть False
        req.user = self.staff
        self.assertFalse(self.ua.has_module_permission(req))
        self.assertFalse(self.ua.has_view_permission(req))
        self.assertFalse(self.ua.has_add_permission(req))
        self.assertFalse(self.ua.has_change_permission(req))
        self.assertFalse(self.ua.has_delete_permission(req))
        # для суперпользователя — True
        req.user = self.superuser
        self.assertTrue(self.ua.has_module_permission(req))
        self.assertTrue(self.ua.has_view_permission(req, obj=None))
        self.assertTrue(self.ua.has_add_permission(req))
        self.assertTrue(self.ua.has_change_permission(req, obj=None))
        self.assertTrue(self.ua.has_delete_permission(req, obj=None))

    def test_groupadmin_permissions(self):
        req = self.factory.get('/')
        req.user = self.staff
        # staff не видит группы
        self.assertFalse(self.ga.has_module_permission(req))
        self.assertFalse(self.ga.has_view_permission(req))
        self.assertFalse(self.ga.has_add_permission(req))
        self.assertFalse(self.ga.has_change_permission(req))
        self.assertFalse(self.ga.has_delete_permission(req))
        # суперпользователь видит и может всё
        req.user = self.superuser
        self.assertTrue(self.ga.has_module_permission(req))
        self.assertTrue(self.ga.has_view_permission(req, obj=None))
        self.assertTrue(self.ga.has_add_permission(req))
        self.assertTrue(self.ga.has_change_permission(req, obj=None))
        self.assertTrue(self.ga.has_delete_permission(req, obj=None))


class TagAndWrittenArticleAdminTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.site = admin.AdminSite()
        self.user = User.objects.create_user('u','u@x','pw', is_staff=True)
        # создаём на всякий язык
        self.lang = Language.objects.create(code='en', name='English')
        # теги и статьи
        self.tag = Tag.objects.create(name='t', owner=self.user)
        self.wa1 = WrittenArticle.objects.create(
            title='W', description='', slug='w', content='<p/>',
            language=self.lang, owner=self.user
        )
        # админы
        self.tag_admin = admin.site._registry[Tag].__class__(Tag, self.site)
        self.wa_admin = admin.site._registry[WrittenArticle].__class__(WrittenArticle, self.site)

    def test_tag_queryset_and_exclude(self):
        req = self.factory.get('/')
        req.user = self.user
        qs = self.tag_admin.get_queryset(req)
        # тэг одного юзера виден
        self.assertListEqual(list(qs), [self.tag])
        excl = self.tag_admin.get_exclude(req)
        self.assertIn('owner', excl)

    def test_writtenarticle_queryset_and_exclude(self):
        req = self.factory.get('/')
        req.user = self.user
        qs = self.wa_admin.get_queryset(req)
        self.assertListEqual(list(qs), [self.wa1])
        excl = self.wa_admin.get_exclude(req)
        self.assertIn('owner', excl)
