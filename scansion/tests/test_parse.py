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

class TestCalculateRatios(TestCase):
    @classmethod
    def setUpTestData(cls):
        Word.objects.create(word="wavering")
        Word.objects.create(word="where")
        Word.objects.create(word="an")
        Word.objects.create(word="squirrel")

        StressPattern.objects.create(word=Word.objects.get(word="wavering"), stresses="/uu", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="where"), stresses="u", popularity=11)
        StressPattern.objects.create(word=Word.objects.get(word="where"), stresses="/", popularity=14)
        StressPattern.objects.create(word=Word.objects.get(word="an"), stresses="u", popularity=11)
        StressPattern.objects.create(word=Word.objects.get(word="squirrel"), stresses="/u", popularity=3)
        StressPattern.objects.create(word=Word.objects.get(word="squirrel"), stresses="u/", popularity=4)
        StressPattern.objects.create(word=Word.objects.get(word="squirrel"), stresses="uu", popularity=3)
    
    def test_one_syllable_one_pattern(self):
        s = StressPattern.objects.filter(word=Word.objects.get(word="an"))
        to_check = stress_patterns_most_popular_syllable_count(s)
        self.assertEqual(calculate_ratios(to_check), [0.0833])
    
    def test_one_syllable_multiple_patterns(self):
        s = StressPattern.objects.filter(word=Word.objects.get(word="where"))
        to_check = stress_patterns_most_popular_syllable_count(s)
        self.assertEqual([1.2500], calculate_ratios(to_check))
    
    def test_multiple_syllables_one_pattern(self):
        s = StressPattern.objects.filter(word=Word.objects.get(word="wavering"))
        to_check = stress_patterns_most_popular_syllable_count(s)
        self.assertEqual([2.000, 0.5000, 0.5000], calculate_ratios(to_check))

    def test_multiple_syllables_multiple_patterns(self):
        s = StressPattern.objects.filter(word=Word.objects.get(word="squirrel"))
        to_check = stress_patterns_most_popular_syllable_count(s)
        self.assertEqual([0.5000, 0.7143], calculate_ratios(to_check))

class TestPreliminarySyllableCount(TestCase):
    def test_preliminary_syllable_count(self):
        self.assertEqual(preliminary_syllable_count("squirrel"), 2)
        self.assertEqual(preliminary_syllable_count("undue"), 2)
        self.assertEqual(preliminary_syllable_count("apes"), 2)
        self.assertEqual(preliminary_syllable_count("viol"), 1)
    
class TestAdjustmentForTwoSyllClusters(TestCase):
    def test_diacritical(self):
        self.assertEqual(adjustment_for_two_syll_clusters("plié"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("neé"), 0)

    def test_ao(self):
        self.assertEqual(adjustment_for_two_syll_clusters("chaos"), 1)

    def test_eo(self):
        self.assertEqual(adjustment_for_two_syll_clusters("eon"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("righteous"), 0)

    def test_ia(self):
        self.assertEqual(adjustment_for_two_syll_clusters("diacritical"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("egalitarian"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("electrician"), 0)
        self.assertEqual(adjustment_for_two_syll_clusters("fustian"), 0)

    def test_ie(self):
        self.assertEqual(adjustment_for_two_syll_clusters("tries"), 0)
        self.assertEqual(adjustment_for_two_syll_clusters("quiet"), 1)

    def test_io(self):
        self.assertEqual(adjustment_for_two_syll_clusters("viol"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("perdition"), 0)
        self.assertEqual(adjustment_for_two_syll_clusters("suspicious"), 0)

    def test_iu(self):
        self.assertEqual(adjustment_for_two_syll_clusters("sodium"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("Lucius"), 0)

    def test_ua(self):
        self.assertEqual(adjustment_for_two_syll_clusters("duality"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("quality"), 0)
        self.assertEqual(adjustment_for_two_syll_clusters("guam"), 0)

    def test_ue(self):
        self.assertEqual(adjustment_for_two_syll_clusters("quell"), 0)
        self.assertEqual(adjustment_for_two_syll_clusters("suet"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("cruel"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("due"), 0)

    def test_uo(self):
        self.assertEqual(adjustment_for_two_syll_clusters("duo"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("quote"), 0)

    def test_vowel_ing(self):
        self.assertEqual(adjustment_for_two_syll_clusters("crying"), 1)
        self.assertEqual(adjustment_for_two_syll_clusters("seeing"), 1)

    def test_consonant_y(self):
        self.assertEqual(adjustment_for_two_syll_clusters("mayor"), 1)

    
    