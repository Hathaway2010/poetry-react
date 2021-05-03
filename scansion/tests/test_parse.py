from django.test import TestCase
from scansion.parse import clean, stress_patterns_most_popular_syllable_count, calculate_ratios, preliminary_syllable_count, adjustment_for_two_syll_clusters, silent_final_e, other_silent_e
from scansion.models import Word, StressPattern

class TestClean(TestCase):
    def test_capitalization(self):
        self.assertEqual(clean("ThE"), "the")

    def test_punctuation(self):
        self.assertEqual(clean("way:"), "way")

    def test_e_accented(self):
        self.assertEqual(clean("belovéd"), "belovéd")

class TestStressPatternsMostPopularSyllableCount(TestCase):
    @classmethod
    def setUpTestData(cls):
        Word.objects.create(word="wavering")
        Word.objects.create(word="where")
        Word.objects.create(word="an")
        Word.objects.create(word="every")
        Word.objects.create(word="squirrel")

        StressPattern.objects.create(word=Word.objects.get(word="wavering"), stresses="/uu", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="where"), stresses="u", popularity=11)
        StressPattern.objects.create(word=Word.objects.get(word="where"), stresses="/", popularity=14)
        StressPattern.objects.create(word=Word.objects.get(word="an"), stresses="u", popularity=11)
        StressPattern.objects.create(word=Word.objects.get(word="every"), stresses="/uu", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="every"), stresses="/u", popularity=10)
        StressPattern.objects.create(word=Word.objects.get(word="squirrel"), stresses="/", popularity=9)
        StressPattern.objects.create(word=Word.objects.get(word="squirrel"), stresses="u", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="squirrel"), stresses="/u", popularity=3)
        StressPattern.objects.create(word=Word.objects.get(word="squirrel"), stresses="u/", popularity=3)
        StressPattern.objects.create(word=Word.objects.get(word="squirrel"), stresses="uu", popularity=4)

    def test_single_object_popularity_one(self):
        s = StressPattern.objects.filter(word=Word.objects.get(word="wavering"))
        self.assertEqual([s[0]], stress_patterns_most_popular_syllable_count(s))

    def test_single_object_popularity_many(self):
        s = StressPattern.objects.filter(word=Word.objects.get(word="an"))
        self.assertEqual([s[0]], stress_patterns_most_popular_syllable_count(s))

    def test_two_objects_same_length(self):
        s = StressPattern.objects.filter(word=Word.objects.get(word="where"))
        self.assertEqual([s[0], s[1]], stress_patterns_most_popular_syllable_count(s))

    def test_two_objects_diff_lengths(self):
        s = StressPattern.objects.filter(word=Word.objects.get(word="every"))
        self.assertEqual([s[1]], stress_patterns_most_popular_syllable_count(s))

    def test_multiple_objects_no_winner(self):
        # if there is no winner in popularity between syllable counts,
        # favor those entered later, because old dictionary is likelier
        # to be wrong than humans
        s = StressPattern.objects.filter(word=Word.objects.get(word="squirrel"))
        self.assertEqual([s[2], s[3], s[4]], stress_patterns_most_popular_syllable_count(s))
    