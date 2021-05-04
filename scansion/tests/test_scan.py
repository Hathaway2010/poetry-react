from django.test import TestCase
from scansion.scan import get_stats, poem_stats, original_scan, house_robber_scan, simple_scan, record, syllables
from scansion.models import Word, StressPattern


class TestStats(TestCase):
    @classmethod
    def setUpTestData(cls):
        Word.objects.create(word="the")
        Word.objects.create(word="moon")
        Word.objects.create(word="is")
        Word.objects.create(word="a")
        Word.objects.create(word="wavering")
        Word.objects.create(word="rim")
        Word.objects.create(word="where")
        Word.objects.create(word="one")
        Word.objects.create(word="fish")
        Word.objects.create(word="slips")
        Word.objects.create(word="water")
        Word.objects.create(word="makes")
        Word.objects.create(word="quietness")
        Word.objects.create(word="of")
        Word.objects.create(word="sound")
        Word.objects.create(word="night")
        Word.objects.create(word="an")
        Word.objects.create(word="anchoring")
        Word.objects.create(word="many")
        Word.objects.create(word="ships")
        Word.objects.create(word="homebound")
        Word.objects.create(word="every")

        StressPattern.objects.create(word=Word.objects.get(word="the"), stresses="u", popularity=381)
        StressPattern.objects.create(word=Word.objects.get(word="the"), stresses="/", popularity=4)
        StressPattern.objects.create(word=Word.objects.get(word="moon"), stresses="u", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="moon"), stresses="/", popularity=15)
        StressPattern.objects.create(word=Word.objects.get(word="is"), stresses="u", popularity=89)
        StressPattern.objects.create(word=Word.objects.get(word="is"), stresses="/", popularity=29)
        StressPattern.objects.create(word=Word.objects.get(word="a"), stresses="u", popularity=149)
        StressPattern.objects.create(word=Word.objects.get(word="a"), stresses="/", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="wavering"), stresses="/uu", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="rim"), stresses="u", popularity=2)
        StressPattern.objects.create(word=Word.objects.get(word="rim"), stresses="/", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="where"), stresses="u", popularity=11)
        StressPattern.objects.create(word=Word.objects.get(word="where"), stresses="/", popularity=14)
        StressPattern.objects.create(word=Word.objects.get(word="one"), stresses="u", popularity=15)
        StressPattern.objects.create(word=Word.objects.get(word="one"), stresses="/", popularity=4)
        StressPattern.objects.create(word=Word.objects.get(word="fish"), stresses="u", popularity=2)
        StressPattern.objects.create(word=Word.objects.get(word="fish"), stresses="/", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="slips"), stresses="/", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="water"), stresses="/u", popularity=3)
        StressPattern.objects.create(word=Word.objects.get(word="makes"), stresses="u", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="makes"), stresses="/", popularity=4)
        StressPattern.objects.create(word=Word.objects.get(word="quietness"), stresses="/uu", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="quietness"), stresses="/u/", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="of"), stresses="u", popularity=152)
        StressPattern.objects.create(word=Word.objects.get(word="of"), stresses="/", popularity=60)
        StressPattern.objects.create(word=Word.objects.get(word="sound"), stresses="u", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="sound"), stresses="/", popularity=3)
        StressPattern.objects.create(word=Word.objects.get(word="night"), stresses="u", popularity=2)
        StressPattern.objects.create(word=Word.objects.get(word="night"), stresses="/", popularity=12)
        StressPattern.objects.create(word=Word.objects.get(word="an"), stresses="u", popularity=11)
        StressPattern.objects.create(word=Word.objects.get(word="anchoring"), stresses="/u/", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="many"), stresses="/u", popularity=4)
        StressPattern.objects.create(word=Word.objects.get(word="ships"), stresses="/", popularity=2)
        StressPattern.objects.create(word=Word.objects.get(word="homebound"), stresses="u/", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="every"), stresses="/uu", popularity=1)
        StressPattern.objects.create(word=Word.objects.get(word="every"), stresses="/u", popularity=10)

    def test_capitalization(self):
        print(get_stats("the"))
        self.assertEqual(get_stats("the"), get_stats("THE"))

    def test_punctuation1(self):
        self.assertEqual(get_stats("sound;"), get_stats("sound"))

    def test_punctuation_capitalization(self):
        self.assertEqual(get_stats("Home-bound"), get_stats("homebound"))

    def test_unknown(self):
        self.assertEqual(get_stats("squirrel"), ["?", "?"])

    def test_one_instance(self):
        self.assertEqual(get_stats("an"), [0.0833])

    def test_multiple_instances(self):
        self.assertEqual(get_stats("every"), [11.0000, 0.0909])

    def test_diff_stress_patterns(self):
        self.assertEqual(get_stats("quietness"), [3.0000, 0.3333, 1.0000])

    def test_line_stats(self):
        line = "THE moon is a wavering rim where one fish slips,"
        scansion = [[0.0131, " ", 8.0000, " ", 0.3333,  " ", 0.0133, " ",
                     2.0000, 0.5000, 0.5000, " ", 0.6667, " ", 1.2500, " ",
                     0.3125, " ", 0.6667, " ", 2.0000, " "]]
        self.assertEqual(poem_stats(line), scansion)

    def test_poem_stats(self):
        poem = """THE moon is a wavering rim where one fish slips,
                The water makes a quietness of sound;
                Night is an anchoring of many ships
                Home-bound."""
        scansion = [[0.0131, " ", 8.0000, " ", 0.3333,  " ", 0.0133, " ",
                     2.0000, 0.5000, 0.5000, " ", 0.6667, " ", 1.2500, " ",
                     0.3125, " ", 0.6667, " ", 2.0000, " "],
                    [0.0131, " ", 4.000, 0.2500, " ", 2.500, " ", 0.0133, " ",
                     3.0000, 0.3333, 1.0000, " ", 0.3987, " ", 2.0000, " "],
                    [4.3333, " ", 0.3333, " ", 0.0833, " ", 2.0000, .5000, 2.0000, " ",
                     0.3987, " ", 5.0000, 0.2000, " ", 3.000, " "],
                    [0.5000, 2.0000, " "]]
        self.assertEqual(poem_stats(poem), scansion)
        
    def test_line_with_unknown(self):
        line = "The moon is a wavering squirrel where one fish runs"
        scansion = [[0.0131, " ", 8.0000, " ", 0.3333,  " ", 0.0133, " ",
                     2.0000, 0.5000, 0.5000, " ", "?", "?", " ", 1.2500, " ",
                     0.3125, " ", 0.6667, " ", "?", " "]]
        self.assertEqual(poem_stats(line), scansion)

    def test_original_unambiguous(self):
        self.assertEqual(original_scan("water moon"), "/u / ")

    def test_original_punctuation_capitalization(self):
        self.assertEqual(original_scan("Wa'ter, moon."),
                         original_scan("water moon"))

    def test_original_equal(self):
        self.assertEqual(original_scan("is is"), "? ? ")

    def test_original_unknown(self):
        self.assertEqual(original_scan("squirrel"), "?? ")

    def test_original_unknown_comparison_unstressed(self):
        self.assertEqual(original_scan("the squirrel"), "u ?? ")

    def test_original_unknown_comparison_stressed(self):
        self.assertEqual(original_scan("moon squirrel"), "/ ?? ")

    def test_original_unknown_comparison_ambiguous(self):
        self.assertEqual(original_scan("is squirrel"), "? ?? ")

    def test_end_of_line(self):
        poem = "the moon is\nthe squirrel"
        self.assertEqual(original_scan(poem), "u / u \nu ?? ")

    def test_original_multiline(self):
        poem = "is squirrel\nmoon squirrel\nthe water moon"
        self.assertEqual(original_scan(poem), "? ?? \n/ ?? \nu /u / ")

    def test_house_robber_unambiguous(self):
        self.assertEqual(house_robber_scan("water moon"), "/u / ")

    def test_house_robber_punctuation_capitalization(self):
        self.assertEqual(house_robber_scan("Wa'ter, moon."),
                         house_robber_scan("water moon"))

    def test_house_robber_equal(self):
        self.assertEqual(house_robber_scan("is is"), "u / ")

    def test_house_robber_never_skip_three(self):
        line = "the moon of is the night"
        self.assertEqual(house_robber_scan(line), "u / u / u / ")

    def test_house_robber_find_obvious_anapest(self):
        self.assertEqual(house_robber_scan("water the moon"), "/u u / ")

    def test_house_robber_never_adjacent(self):
        self.assertEqual(house_robber_scan("moon water"), "/ u/ ")

    def test_house_robber_unknown(self):
        self.assertEqual(house_robber_scan("squirrel"), "u/ ")

    def test_house_robber_unstressed_unknown(self):
        self.assertEqual(house_robber_scan("the bird"), "u / ")

    def test_house_robber_stressed_unknown(self):
        self.assertEqual(house_robber_scan("moon bird"), "/ u ")

    def test_simple_unambiguous(self):
        self.assertEqual(simple_scan("water moon"), "/u / ")

    def test_simple_punctuation_capitalization(self):
        self.assertEqual(simple_scan("Wa'ter, moon."),
                         simple_scan("water moon"))
    
    def test_simple_scan_equal(self):
        self.assertEqual(simple_scan("is is"), "u u ")

    def test_simple_scan_unknown(self):
        self.assertEqual(simple_scan("squirrel"), "?? ")

    def test_record_unknown(self):
        record("cat", "/")
        w = Word.objects.filter(word="cat")
        self.assertEqual(w.count(), 1)
        self.assertEqual(w[0].popularity, 1)
        self.assertEqual(w[0].syllables, 1)
        s = StressPattern.objects.filter(word=w[0])
        self.assertEqual(s.count(), 1)
        self.assertEqual(s[0].stresses, "/")
        self.assertEqual(s[0].popularity, 1)
        
    def test_record_known(self):
        record("moon", "/")
        w = Word.objects.filter(word="moon")
        self.assertEqual(w.count(), 1)
        self.assertEqual(w[0].popularity, 0)
        s = StressPattern.objects.filter(word=w[0]).order_by("-popularity")
        self.assertEqual(s.count(), 2)
        self.assertEqual((s[0].stresses, s[0].popularity), ("/", 16))
        self.assertEqual((s[1].stresses, s[1].popularity), ("u", 1))

    def test_capitalization_punctuation(self):
        record("Mo'on", "/")
        w = Word.objects.filter(word="moon")
        self.assertEqual(w.count(), 1)
        self.assertEqual(w[0].popularity, 0)
        s = StressPattern.objects.filter(word=w[0]).order_by("-popularity")
        self.assertEqual(s[0].popularity, 16)

    def test_record_new_pron(self):
        record("wavering", "/u/")
        w = Word.objects.filter(word="wavering")
        self.assertEqual(w.count(), 1)
        self.assertEqual(w[0].popularity, 0)
        s = StressPattern.objects.filter(word=w[0])
        self.assertEqual(s.count(), 2)
        self.assertEqual((s[0].stresses, s[0].popularity,
                          s[1].stresses, s[1].popularity),
                         ("/uu", 1, "/u/", 1))

class TestSyllable(TestCase):
    # see test_parse for more detailed tests
    def test_simple(self):
        self.assertEqual(syllables("squirrel"), 2)
    
    def test_two_syll_cluster(self):
        self.assertEqual(syllables("diana"), 3)

    def test_silent_final_e(self):
        self.assertEqual(syllables("make"), 1)

    def test_other_silent_e(self):
        self.assertEqual(syllables("lonely"), 2)

    def test_would_be_zero(self):
        self.assertEqual(syllables("the"), 1)

    def test_combine(self):
        # add more of these as they come up
        self.assertEqual(syllables("violate"), 3)
        