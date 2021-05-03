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
    # get version of word without non-alphabetic characters and lowercase
    w = parse.clean(word)
    print(w)
    
    try:
        word_instance = Word.objects.get(word=w)
        s = StressPattern.objects.filter(word=word_instance)
        if s.exists():
            stresses = parse.stress_patterns_most_popular_syllable_count(s)
            return parse.calculate_ratios(stresses)
        elif word_instance.syllables:
            return ["?" for i in range(word_instance.syllables)]
        else:
            return ["?" for i in range(syllables(w))]           
    except Word.DoesNotExist:
        return ["?" for i in range(syllables(w))]

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
    lines = parse.NEWLINE.split(poem)
    poem_list = []
    # for each line get the list of stress probabilities (stressed / unstressed)
    # for each word and extend stress list with that sublist; for spaces, append a space
    for line in lines:
        words = line.split()
        line_list = []
        for word in words:
            stress = get_stats(word)
            line_list.extend(stress)
            line_list.append(" ")
        poem_list.append(line_list)
    return poem_list


def house_robber_scan(poem):
    pass

def original_scan(poem):
    pass

def simple_scan(poem):
    pass

def record(poem, scansion):
    pass

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
    w = parse.clean(word)
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
    if count == 0:
        count += 1
    return count
