from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTest(TestCase):
    """Test admin side methods working"""

    def setUp(self):
        """Setup method will be available to every method"""

        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@test.com",
            password="admintestpass123"
        )

        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email="test@user.com",
            name="user",
            password="userpass123"
        )

    def test_user_listed(self):
        """test created user listed in user list"""

        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_user_edit_page(self):
        """Test user edit page available"""

        # Thsi args value retuns the value and add it at the end of the url
        # ie. /admin/core/user/user_id
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_user_create_page(self):
        """test user creae page available"""

        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
