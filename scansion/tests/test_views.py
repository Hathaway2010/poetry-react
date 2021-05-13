from django.test import TestCase
from django.test import Client
from django.urls import reverse

from scansion.views import index, about, choose_poem, login, logout, register 
from scansion.models import User, Word, StressPattern, Poet, Poem, Algorithm, HumanScansion, MachineScansion

client = Client()

class TestIndexGet(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poet.objects.create(last_name="SHAKESPEARE")
        Poem.objects.create(poem="moon squirrel")
        Algorithm.objects.create(name="Simple Scan")
        Algorithm.objects.create(name="House Robber Scan", preferred=True)
        User.objects.create_user("someone", password="12345", score=10)
        User.objects.create_user("squirrel", password="password", score=9)

    def test_not_authenticated(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("scansion/layout.html")
        self.assertTemplateUsed("scansion/index.html")
        self.assertEqual(response.context["poem"].title, "A Sea Dirge")
        self.assertEqual(response.context["algorithms"].count(), 2)
        self.assertEqual(len(response.context["scansions"]), 2)

    def test_not_promoted(self):
        self.client.login(username="squirrel", password="password")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["poem"].title, "A Sea Dirge")
        self.assertEqual(response.context["algorithms"].count(), 2)
        self.assertEqual(len(response.context["scansions"]), 2)

    def test_promoted(self):
        self.client.login(username="someone", password="12345")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["poem"].poem, "moon squirrel")
        self.assertEqual(response.context["algorithms"].count(), 2)
        self.assertEqual(len(response.context["scansions"]), 2)


class TestIndexPut(TestCase):
    pass

class TestAbout(TestCase):
    def test_about(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("scansion/layout.html")
        self.assertTemplateUsed("scansion/about.html")

class TestChoosePoem(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poem.objects.create(poem="moon squirrel")
    
    def test_choose_poem(self):
        response = self.client.get(reverse("choose_poem"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("scansion/layout.html")
        self.assertTemplateUsed("scansion/choose_poem.html")
        self.assertEqual(response.context["human_list"].count(), 0)
        self.assertEqual(response.context["computer_list"].count(), 1)