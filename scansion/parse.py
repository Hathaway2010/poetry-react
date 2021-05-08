"""MODULE PARSE
   ============
   This module contains helper functions for scan.py and other files.

   Functions
   ---------
   clean_poem(poem) : Return poem with dashes replaced by spaces
   clean(word) : Return word processed for lookup
   make_dict(scansion): Turn string scansion into dictionary
   make_dict_p(poem): Turn string poem into dictionary
   make_string(scansion): Turn dict scansion into string
   syllable_counter(stress_pattern_queryset) : Find popular syll counts
   calculate_ratios(word) : Find stressed / unstressed for syllables
   preliminary_syllable_count(word): Count vowel clusters
   adjustment_for_two_syll_clusters(word): Count 2-syll vowel clusters
   silent_final_e: Return True if silent final e, False otherwise
   other_silent_e: Return True if other silent e, False otherwise
   """

import re

# regexes to reuse in other modules
NEWLINE = re.compile("\r\n|\n|\r")
DISALLOWED = re.compile("[^-A-Za-zé]")
DASH = re.compile(" *-- *| *– *| *— *")
SLASH = re.compile(" */ *")

# scansion symbols 
UNKNOWN = "?"
UNSTRESSED = "u"
STRESSED = "/"

def clean_poem(poem):
    """Return poem replacing dashes and slashes with spaces"""
    dashless = re.sub(DASH, " ", poem)
    dashless_slashless = re.sub(SLASH, " ", dashless)
    return dashless_slashless

def clean(word):
    """Return word lowercase and without nonalphabetic characters"""
    w = re.sub(DISALLOWED, "", word)
    return w.lower()

def make_dict(scansion):
        """Make dict id-ing scansion's words by line, word index"""
        if not scansion:
            return ""
        else:
            line_word_dict = {}
            for i, line in enumerate(scansion.splitlines()):
                line_word_dict[i] = {}
                for j, word in enumerate(line.split()):
                    line_word_dict[i][j] = word
            return line_word_dict
    
def make_dict_p(poem):
    """make dict id-ing poem's words by line, word index"""
    p = clean_poem(poem)
    line_word_dict = {}
    for i, line in enumerate(poem.splitlines()):
        line_word_dict[i] = {}
        relevant_words = [word for word in line.split() if clean(word)]
        for j, word in enumerate(relevant_words):
            line_word_dict[i][j] = word
    return line_word_dict

def make_string(scansion_dict):
    s = ""
    for line in scansion_dict:
        for word in scansion_dict[line]:
            s = s + scansion_dict[line][word] + " "
        s += "\n"
    return s

def syllable_counter(stress_pattern_queryset):
    """Find StressPatterns with most popular syllable count

    Parameters
    ----------
    stress_pattern_queryset : Django queryset
        queryset of StressPattern objects for a given word

    Returns
    -------
    stress_pattern_list : list
        list of StressPattern objects with most popular syllable count

    max_popularity : int
        popularity of most popular syllable count

    most_popular_count : int
        most popular syllable count
    """
    count_dict = {}
    max_popularity = 0
    most_popular_count = 0

    for pattern in stress_pattern_queryset:
        count = pattern.get_syllable_count()
        if count in count_dict:
            count_dict[count][0].append(pattern)
            count_dict[count][1] += pattern.popularity
        else:
            count_dict[count] = [[pattern], pattern.popularity]
        if max_popularity <= count_dict[count][1]:
                max_popularity = count_dict[count][1]
                most_popular_count = count
    
    stress_pattern_list = count_dict[most_popular_count][0]
    return stress_pattern_list, max_popularity, most_popular_count
    
def calculate_ratios(stress_pattern_list):
    """Find ratio stressed / unstressed for each syllable in word
    
    Parameters
    ----------
    stress_pattern_list : list
        list of StressPattern objects for a word
        (stress patterns in list must be of uniform length,
        produced by stress_patterns_most_popular_syllable_count)

    Returns
    -------
    value_list : list
        ratio of times scanned stressed/unstressed
        for each syllable in word,
        rounded to 4 decimal places
    """
    length = stress_pattern_list[0].get_syllable_count()
    value_list = []
    for i in range(length):
        stressed = 1
        unstressed = 1
        for pattern in stress_pattern_list:
            if pattern.stresses[i] == STRESSED:
                stressed += pattern.popularity
            elif pattern.stresses[i] == UNSTRESSED:
                unstressed += pattern.popularity
        value_list.append(round(stressed / unstressed, 4))
    return value_list

def preliminary_syllable_count(word):
    """Count clusters of 1 or more vowels (each likely a syllable)"""
    vowels_or_vowel_clusters = re.findall("[AEÉIOUaeéiouy]+", word)
    return len(vowels_or_vowel_clusters)

def adjustment_for_two_syll_clusters(word):
    """Count clusters of vowels likely to have 2 syllables, not 1"""
    # This is massive and not intuitive. Examples of what it's doing can be found in tests/test_parse.py
    two_syllable_clusters = re.findall("[aiouy]é|ao|eo[^u]|ia[^n]|[^ct]ian|iet|io[^nu]|[^c]iu|[^gq]ua|[^gq]ue[lt]|[^q]uo|[aeiouy]ing|[aeiou]y[aiou]", word) # exceptions: Preus, Aida, poet, luau)
    return len(two_syllable_clusters)

def silent_final_e(word):
    """Return true if there is likely a silent final e"""
    # e is usually silent at the ends of word
    # but there are exceptions like "cable,"
    # "cadre," and "untrue"
    audible_final_e = re.compile('[^aeiouylrw]le$|[^aeiouywr]re$|[aeioy]e|[^g]ue')
    if word[-1] == "e" and not audible_final_e.search(word):
        return True
    return False

def other_silent_e(word):
    """Return true if other 'e's near end are likely silent"""
    # final -ed or -es unlikely to represent its own syllable
    silent_final_ed_es = re.compile("[^aeiouydlrt]ed$|[^aeiouycghjlrsxz]es$|thes$|[aeiouylrw]led$|[aeiouylrw]les$|[aeiouyrw]res$|[aeiouyrw]red$")
    # e in the middle unlikely to represent a syllable
    # as in 'lonely' or 'surely'
    consonant_e_ly = re.compile("[^aeiouy]ely$")
    # If I find ways to identify other silent 'e's in words,
    # like the 'e' in 'sometimes' or the first in 'nonetheless'
    # this function may be expanded
    if silent_final_ed_es.search(word) or consonant_e_ly.search(word):
        return True
    return False