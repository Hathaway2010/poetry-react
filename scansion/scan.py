"""MODULE SCAN
===============
This module scans poems and records users' scansions.

Functions
---------

get_stats(word, confidence=False) : Return ratio to calculate scansion.
poem_stats(poem) : Use get_stats on whole poem and return nested list.
original_scan(poem) : Scan by comparing each ratio to the next.
house_robber_scan(poem) : Scan with solution to house robber problem
simple_scan(poem) : Scan based on ratios with no comparisons.
record(poem, scansion) : Record new user scansions in database.
syllables(word) : Guess syllable count of word not in database.
"""

from copy import copy
from collections import Counter
from . import parse
from .models import Word, StressPattern

def get_stats(word):
    """Get ratio of stressed scansions to unstressed for word's syllables.
    
    Arguments
    ---------
    word : str
        word for which stats need to be looked up

    Returns
    -------
    values : list of floats
        stress ratio for each syllable of the word; 4 decimal places
        `?` if unknown
    """    
    try:
        word_instance = Word.objects.get(word=word)
        s = StressPattern.objects.filter(word=word_instance)
        if s.exists():
            stresses = parse.syllable_counter(s)[0]
            return parse.calculate_ratios(stresses)
        elif word_instance.syllables:
            return ["?" for i in range(word_instance.syllables)]
        else:
            return ["?" for i in range(syllables(word))]           
    except Word.DoesNotExist:
        return ["?" for i in range(syllables(word))]

def poem_stats(poem):
    """Find stress ratio for each word in a poem.

    Parameters
    ----------
    poem : str
        poem to scan
   
    Returns
    -------
    stress_list : list
        list of lists of stress ratios
    """
    # split poem into lines
    cleaned_poem = parse.clean_poem(poem)
    lines = parse.NEWLINE.split(cleaned_poem)
    poem_list = []
    # for each line get the list of stress probabilities (stressed / unstressed)
    # for each word and extend stress list with that sublist; for spaces, append a space
    for line in lines:
        words = line.split()
        line_list = []
        for word in words:
            # get version of word without non-alphabetic characters and lowercase
            w = parse.clean(word)
            if w:
                stress = get_stats(w)
                line_list.extend(stress)
                line_list.append(" ")
        poem_list.append(line_list)
    return poem_list

def original_scan(poem):
    """Scan poem by comparing each stress ratio to the next.
    
    Parameters
    ----------
    poem : str
        poem to scan
        
    Return
    ------
    poem_scansion : str
        scansion with lines separated by newlines, words by spaces
    """
    stress_list = poem_stats(poem)
    poem_scansion = []
    # for each line in this, compare the stress ratio for each word to the next
    for line in stress_list:
        line_scansion = ""
        
        # function to compare two vlues
        def comp(value1, value2):
            """Assign stress symbol based on ratio comparison.

            Parameters
            ----------
            value1 : float
                value to the left in the line
            
            value2 : float
                value immediately to its right
            
            Returns
            -------

            symbol : str
                single character indicating stressed (`/`), 
                unstressed (`u`) or unknown (`?`)
            """
            # if the second value is unknown, guess the first based on itself alone
            if value2 == "?":
                if value1 < 0.2:
                    return "u"
                elif value >= 1.0:
                    return "/"
                else:
                    return "?"
            # otherwise, if the first is smaller, guess unstressed, or "u"
            elif value1 < value2:
                return "u"
            # if the first is larger, guess stressed, or "/"
            elif value1 > value2:
                return "/"
            # if they are equal, decline to make a guess
            else:
                return "?"
        # check that the line is not blank (that is, a stanza break)
        
        if line:
            for i, value in enumerate(line):
                # for each value, if that value is non-numeric, simply add it,
                # whether it is a space (indicating a space in the poem), or a "?"
                if value in ["?", " "]:
                    line_scansion += value
                # otherwise, if we are not nearing the end of the line,
                # compare each to the next
                elif i < len(line) - 2:
                    if line[i + 1] == " ":
                        line_scansion += comp(value, line[i + 2])
                    else:
                        line_scansion += comp(value, line[i + 1])
                # finally, if we are near the end of the line,
                # compare to the previous syllable
                else:
                    if line[i - 1] != " ":
                        line_scansion += comp(value, line[i - 1])
                    else:
                        line_scansion += comp(value, line[i - 2])
        poem_scansion.append(line_scansion)
    return "\n".join(poem_scansion)

def house_robber_scan(poem):
    """Scan poem by finding max sum of ratios with no adjacent stresses
    
    Parameters
    ----------
    poem : str
        poem to scan
    
    Returns
    -------
    scansion : str
        scansion with lines separated by newlines, words by spaces        
    """
    # get stress pattern of poem
    stress_list = poem_stats(poem)
    poem_scansion = []
    for line in stress_list:
        # remove spaces and replace question marks with a guess of 0.3
        # add each value to a tuple containing its index as the second value
        spaceless_line = []
        for i, value in enumerate(line):
            if value != " ":
                if value == "?":
                    spaceless_line.append((0.3, i))
                else:
                    spaceless_line.append((value, i))
        # initialize two lists to represent potential stress patterns for the lines
        prev1 = []
        prev2 = []
        # iterate through spaceless line so constructed
        for pair in spaceless_line:
            tmp = copy(prev1)
            # https://stackoverflow.com/questions/25047561/finding-a-sum-in-nested-list-using-a-lambda-function
            # if the sum of stress values contained in prev1 is less than the sum
            # of stress values in prev2 + the current stress value
            # make prev1 a copy of prev2
            if sum(p[0] for p in prev1) <= sum(p[0] for p in prev2) + pair[0]:
                prev2.append(pair)
                prev1 = copy(prev2)
            # either way, make the previous prev1 prev2
            prev2 = copy(tmp)
        # iterate through original line, adding to a scansion
        line_scansion = ""
        for i, value in enumerate(line):
            # carry spaces over into the scansion untouched
            if value == " ":
                line_scansion += value
            # otherwise, if a given value is an index included in prev1,
            # which is the "winner" for highest values
            # make it stressed, and if it is not, make it unstressed
            elif [pair for pair in prev1 if pair[1] == i]:
                line_scansion += "/"
            else:
                line_scansion += "u"
        poem_scansion.append(line_scansion)
    return "\n".join(poem_scansion)

def simple_scan(poem):
    """Scan poem using ratios but not comparing them
    
    Parameters
    ----------
    poem : str
        poem to scan
    
    Returns
    -------
    scansion : str
        scansion with lines separated by newlines, words by spaces
    """
    stats = poem_stats(poem)
    poem_scansion = []
    for line in stats:
        line_scansion = ""
        if line:
            for value in line:
                if value in [" ", "?"]:
                    line_scansion += value
                elif value > 1:
                    line_scansion += "/"
                else:
                    line_scansion += "u"
        poem_scansion.append(line_scansion)
    return "\n".join(poem_scansion)

def simple_scan_augmented(poem):
    """Scan poem using ratios but not comparing them
    
    Parameters
    ----------
    poem : str
        poem to scan
    
    Returns
    -------
    scansion : str
        scansion with lines separated by newlines, words by spaces
    """
    stats = poem_stats(poem)
    poem_scansion = []
    for line in stats:
        line_scansion = ""
        if line:
            for value in line:
                if value in [" ", "?"]:
                    line_scansion += value
                elif value > 1:
                    line_scansion += "/"
                else:
                    line_scansion += "u"
        poem_scansion.append(line_scansion)
    return "\n".join(poem_scansion)
def reconcile(authoritative, scansion_queryset, diffs):
    """Reconcile new human scansion with others
    
    Parameters
    ----------
    authoritative: str
        poem's authoritative scansion as string
    scansion_queryset: Django queryset
        other human scansion objects for that poem, incl new scansion
    
    Returns
    -------
    authoritative: str
        reconciliation between old and new scansions"""
    # if there's only one previous human scansion
    # differences will be ties; decide in favor of new;
    # if scansion and authoritative are identical,
    # (i.e. no diffs) return scansion
    if scansion_queryset.count() <= 2 or not diffs:
        return authoritative
    else:
        old_s_dicts = [parse.make_dict(hs.scansion) for hs in scansion_queryset]
        auth_s_dict = parse.make_dict(authoritative)
        for diff in diffs:
            print(f"diff line {diff[0]} word {diff[1]}")
            line_number = int(diff[0])
            word_number = int(diff[1])
            variants = [scan_dict[line_number][word_number] for scan_dict in old_s_dicts]
            # https://stackoverflow.com/questions/23033625/sorting-counter-collection-in-python-with-secondary-term-tie-breaker
            c = sorted(Counter(variants).most_common(), key = lambda x: (-x[1], variants[::-1].index(x[0])))
            auth_s_dict[line_number][word_number] = c[0][0]
        return parse.make_string(auth_s_dict)



            

def record(poem, scansion):
    """Record user scansions of individual words in database
    
    Parameters
    ----------
    poem : str
        poem that was scanned
    scansion : str
        scansion, words separated with spaces, lines with newlines
    """
    # split both poem and scansion on spaces
    words = poem.split()
    cleaned_words = [parse.clean(word) for word in words]
    scanned_words = scansion.strip().split()
    # find each word in the database if it is there
    for i, word in enumerate(cleaned_words):
        w = Word.objects.filter(word=word)
        if w.exists():
            if w.count() > 1:
                print("dupllicate word")    
            # see if any instances of the word have the user-inputted stress pattern
            s = StressPattern.objects.filter(word=w[0], stresses=scanned_words[i])
            if s.exists():
                if s.count() > 1:
                    print("duplicate stress patterns")
                sp = s[0]
                sp.popularity += 1
                sp.save()
            else:
                sp = StressPattern(word=w[0], stresses=scanned_words[i], popularity=1)
                sp.save()
        else:
            wd = Word(word=word, popularity=1, syllables=len(scanned_words[i]))
            wd.save()
            sp = StressPattern(word=wd, stresses=scanned_words[i], popularity=1)
            sp.save()

def syllables(word):
    """Guess syllable count of word not in database.

    Parameters
    ----------
    word : str
        word not found in database
    
    Returns
    -------
    count : int
        estimated number of syllables
    
    See also
    --------
    tests/test_scan.py to clarify regular expressions
    """   
    cleaned_word = parse.clean(word)
    compound = cleaned_word.split("-")
    total_count = 0
    for w in compound:
        # get preliminary count by counting vowels or clusters thereof
        count = parse.preliminary_syllable_count(w)
        # increment count for all vowel clusters likely to be 2 syllables
        count += parse.adjustment_for_two_syll_clusters(w)
        # subtract 1 for every likely silent e
        if parse.silent_final_e(w):
            count -= 1
        if parse.other_silent_e(w):
            count -= 1
            # words have at least one syllable
        if count <= 0:
            count = 1
        total_count += count
    return total_count
