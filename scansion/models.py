from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date

from . import parse

# Create your models here.
class User(AbstractUser):
    score = models.IntegerField(default=0)
    def is_promoted(self):
        return self.score >= 10

    def __str__(self):
        return f"{self.username}, Promoted: {self.is_promoted()}"

class Word(models.Model):
    PARTS_OF_SPEECH = [("", "Unknown/ambiguous"),
                       ("n", "Noun"), 
                       ("v", "Verb"), 
                       ("a", "Adjective"), 
                       ("adv", "Adverb"), 
                       ("pro", "Pronoun"), 
                       ("pre", "Preposition"), 
                       ("con", "Conjunction"), 
                       ("art", "Article"), 
                       ("int", "Interjection")]
    word = models.CharField(max_length=50)
    popularity = models.IntegerField(default=0)
    # "pronunciation" fr/ Websters1913 (syllable splits and accents)
    # eventually I may get real pronunciations from, e.g., wiktionary
    pronunciation_line = models.CharField(max_length=70, blank=True)
    syllables = models.IntegerField(null=True, blank=True)
    part_of_speech = models.CharField(max_length=3, choices=PARTS_OF_SPEECH, default="")

    def __str__(self):
        return self.word

class StressPattern(models.Model):
    word = models.ForeignKey(Word, on_delete=models.PROTECT)
    stresses = models.CharField(max_length=20)
    popularity = models.IntegerField(default=1)

    def is_valid(self):
        for char in self.stresses:
            if char not in [" ", parse.UNKNOWN, parse.STRESSED, parse.UNSTRESSED]:
                return False
        return True
    
    def get_syllable_count(self):
        return len(self.stresses)

    def __str__(self):
        return f"{self.word.word}, {self.stresses}, popularity: {self.popularity}"

class Poet(models.Model):
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)
    birth = models.IntegerField(blank=True, null=True)
    death = models.IntegerField(blank=True, null=True)
    bio = models.TextField(blank=True)


    def is_valid(self):
        now = int(date.today().strftime("%Y"))
        if self.birth and self.death:
            return self.birth < self.death and self.death < now
        elif self.birth:
            return self.birth < now
        elif self.death:
            return self.death <= now
        else:
            return True

    def __str__(self):
        return f"{self.last_name}"

class Poem(models.Model):
    title = models.TextField(blank=True)
    poet = models.ForeignKey(Poet, on_delete=models.SET_NULL, blank=True, null=True)
    scansion = models.TextField(blank=True)
    poem = models.TextField()
    
    def first_line(self):
        first_line_end = parse.NEWLINE.search(self.poem)
        print(first_line_end)
        if first_line_end:
            return self.poem[: first_line_end.start()]
        else:
            return self.poem

    def has_valid_scansion(self):
        for char in self.scansion:
            if char not in [" ", parse.STRESSED, parse.UNSTRESSED, "\n", "\r", "\r\n"]:
                print(f"{char} not allowed in scansion")
                return False
        return True

    def __str__(self):
        if self.title:
            t = self.title
        else:
            t = self.first_line()
        if self.poet:
            return f"{t} by {self.poet.last_name}"
        else:
            return t

class Algorithm(models.Model):
    name = models.CharField(max_length=50)
    about = models.TextField(blank=True)
    preferred = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}, preferred: {self.preferred}"

class HumanScansion(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE)
    scansion = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def is_valid(self):
        for char in self.scansion:
            if char not in [" ", parse.STRESSED, parse.UNSTRESSED, "\n", "\r", "\r\n"]:
                return False
        return True
    
    def __str__(self):
        return f"User{self.user.id}'s scansion of {self.poem.__str__()}"

class MachineScansion(models.Model):
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE)
    scansion = models.TextField()
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    
    def is_valid(self):
        for char in self.scansion:
            if char not in [" ", parse.UNKNOWN, parse.STRESSED, parse.UNSTRESSED, "\n", "\r", "\r\n"]:
                return False
        return True

    def __str__(self):
        return f"{self.algorithm.name} scansion of {self.poem.__str__()}"
