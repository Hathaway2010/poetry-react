from django.test import TestCase
from scansion.models import User, Word, StressPattern, Poet, Poem, Algorithm, HumanScansion, MachineScansion

class TestUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username="someone")
        User.objects.create(username="someoneelse", score=10)

    def test_user_not_promoted(self):
        u = User.objects.filter(username="someone")
        self.assertTrue(u.exists())
        self.assertEqual(u[0].score, 0)
        self.assertFalse(u[0].is_promoted())
        self.assertEqual(u[0].__str__(), "someone, Promoted: False")

    def test_user_promoted(self):
        u = User.objects.filter(username="someoneelse")
        self.assertTrue(u.exists())
        self.assertEqual(u[0].score, 10)
        self.assertTrue(u[0].is_promoted())
        self.assertEqual(u[0].__str__(), "someoneelse, Promoted: True")
        
class TestWord(TestCase):
    @classmethod
    def setUpTestData(cls):
        Word.objects.create(word="squirrel")
        Word.objects.create(word="rabbit", popularity=1, syllables=2, part_of_speech="n")

    def test_word_defaults(self):
        w = Word.objects.filter(word="squirrel")
        self.assertTrue(w.exists())
        self.assertEqual(w[0].popularity, 0)
        self.assertIsNone(w[0].syllables)
        self.assertEqual(w[0].part_of_speech, "")
        self.assertEqual(w[0].pronunciation_line, "")
        self.assertEqual(w[0].__str__(), "squirrel")

    def test_word_values(self):
        w = Word.objects.filter(word="rabbit")
        self.assertTrue(w.exists())
        self.assertEqual(w[0].popularity, 1)
        self.assertEqual(w[0].syllables, 2)
        self.assertEqual(w[0].part_of_speech, "n")
        self.assertEqual(w[0].__str__(), "rabbit")

class TestStressPattern(TestCase):
    @classmethod
    def setUpTestData(cls):
        Word.objects.create(id=1, word="squirrel", popularity=2)
        StressPattern.objects.create(word=Word.objects.get(word="squirrel"), stresses="squirrel")
        StressPattern.objects.create(word=Word.objects.get(word="squirrel"), stresses="/u")
    
    def test_stresspattern_valid(self):
        s = StressPattern.objects.filter(word=Word.objects.get(word="squirrel"))
        self.assertEqual(s.count(), 2)
        self.assertEqual(s[1].word.word, "squirrel")
        self.assertEqual(s[1].popularity, 1)
        self.assertEqual(s[1].get_syllable_count(), 2)
        self.assertTrue(s[1].is_valid())
        self.assertEqual(s[1].__str__(), "squirrel, /u, popularity: 1")
    
    def test_stresspattern_invalid(self):
        s = StressPattern.objects.filter(word=Word.objects.get(word="squirrel"))
        self.assertFalse(s[0].is_valid())
        self.assertEqual(s[0].__str__(), "squirrel, squirrel, popularity: 1")

class TestPoet(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poet.objects.create(last_name="Shakespeare")
        Poet.objects.create(first_name="Jane", last_name="Doe", birth=2000, death=1952, bio="Lived backward like Merlin!")
        Poet.objects.create(first_name="Jane", last_name="Doe", birth=3000, bio="Poets of the future!")
        Poet.objects.create(first_name="Jane", last_name="Doe", death=3000, bio="Not dead yet.")
        Poet.objects.create(first_name="Jane", last_name="Doe", birth=2000, death=3000, bio="Still not dead yet.")
    
    def test_poet_defaults(self):
        p = Poet.objects.filter(last_name="Shakespeare")
        self.assertEqual(p.count(), 1)
        for trait in [p[0].first_name, p[0].birth, p[0].death, p[0].bio]:
            self.assertTrue(trait is None or trait=="")
        self.assertTrue(p[0].is_valid())
        self.assertEqual(p[0].__str__(), "Shakespeare")
        
    def test_poets__invalid(self):
        p = Poet.objects.filter(last_name="Doe")
        self.assertEqual(p.count(), 4)
        for poet in p:
            self.assertFalse(poet.is_valid())
            self.assertEqual(poet.__str__(), "Doe")
    
class TestPoem(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poet.objects.create(last_name="Shakespeare")
        Poem.objects.create(poem="moon squirrel")
        Poem.objects.create(title="A Sea Dirge", poet=Poet.objects.get(last_name="Shakespeare"), poem="""Full fathom five thy father lies:
Of his bones are coral made;
Those are pearls that were his eyes:
Nothing of him that doth fade,
But doth suffer a sea-change
Into something rich and strange;
Sea-nymphs hourly ring his knell:
Hark! now I hear them,--
Ding, dong, Bell.""", scansion="""u /u / u /u /
/ u / u /u /
/ u / u / u /
/u / u / u /
u u /u u /u
/u /u / u /
/u /u / u /
/ u u / u
/ u /""")

    def test_poem_defaults(self):
        p = Poem.objects.filter(poem="moon squirrel")
        self.assertEqual(p.count(), 1)
        self.assertEqual(p[0].title, "")
        self.assertIsNone(p[0].poet)
        self.assertEqual(p[0].scansion, "")
        self.assertTrue(p[0].has_valid_scansion)
        self.assertEqual(p[0].first_line(), "moon squirrel")
        self.assertEqual(p[0].__str__(), "moon squirrel")

    def test_poem_values(self):
        p = Poem.objects.filter(title="A Sea Dirge")
        self.assertEqual(p.count(), 1)
        self.assertTrue(p[0].has_valid_scansion())
        self.assertEqual(p[0].poet.last_name, "Shakespeare")
        self.assertEqual(p[0].first_line(), "Full fathom five thy father lies:")
        self.assertEqual(p[0].__str__(), "A Sea Dirge by Shakespeare")

class TestAlgorithm(TestCase):
    @classmethod
    def setUpTestData(cls):
        Algorithm.objects.create(name="Original Scan")
        Algorithm.objects.create(name="House Robber Scan", about="An algorithm", preferred=True)

    def test_algorithm_defaults(self):
        a = Algorithm.objects.filter(name="Original Scan")
        self.assertEqual(a[0].about, "")
        self.assertFalse(a[0].preferred)
        self.assertEqual(a[0].__str__(), "Original Scan, preferred: False")

    def test_algorithm_values(self):
        a = Algorithm.objects.filter(name="House Robber Scan")
        self.assertEqual(a[0].about, "An algorithm")
        self.assertTrue(a[0].preferred)
        self.assertEqual(a[0].__str__(), "House Robber Scan, preferred: True")

class TestHumanScansion(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create(username="someone", score=10)
        User.objects.create(username="someoneelse", score=10)
        Poem.objects.create(poem="moon squirrel")
        HumanScansion.objects.create(
            poem=Poem.objects.get(poem="moon squirrel"), scansion="/ uu", user=User.objects.get(username="someone")
        )
        HumanScansion.objects.create(
            poem=Poem.objects.get(poem="moon squirrel"), scansion="afds", user=User.objects.get(username="someoneelse") 
        )

    def test_human_scansion_valid(self):
        hs = HumanScansion.objects.all()
        self.assertEqual(hs.count(), 2)
        self.assertTrue(hs[0].is_valid())
        self.assertEqual(hs[0].__str__(), "User1's scansion of moon squirrel")
    
    def test_human_scansion_invalid(self):
        hs = HumanScansion.objects.all()
        self.assertFalse(hs[1].is_valid())

class TestMachineScansion(TestCase):
    @classmethod
    def setUpTestData(cls):
        Poem.objects.create(poem="moon squirrel")
        Algorithm.objects.create(name="Buggy Algorithm")
        Algorithm.objects.create(name="House Robber Algorithm")
        MachineScansion.objects.create(
            poem=Poem.objects.get(poem="moon squirrel"), scansion="saf;jd", algorithm=Algorithm.objects.get(name="Buggy Algorithm")
        )
        MachineScansion.objects.create(
            poem=Poem.objects.get(poem="moon squirrel"), scansion="/ u/", algorithm=Algorithm.objects.get(name="House Robber Algorithm")
        )
    def test_machine_scansion_valid(self):
        ms = MachineScansion.objects.all()
        self.assertEqual(ms.count(), 2)
        self.assertTrue(ms[1].is_valid())
        self.assertEqual(ms[1].__str__(), "House Robber Algorithm scansion of moon squirrel")


    def test_machine_scansion_invalid(self):
        ms = MachineScansion.objects.all()
        self.assertFalse(ms[0].is_valid())
