from django.shortcuts import HttpResponseRedirect, render
from django.http import HttpResponse
from django.urls import reverse
# https://www.kite.com/python/docs/django.contrib.admindocs.views.staff_member_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from django.template.defaulttags import register

import random
import json
from random import choice

from .models import User, Word, StressPattern, Poet, Poem, Algorithm, HumanScansion, MachineScansion
from . import scan
from . import parse

ALGORITHMS = {"House Robber Scan": scan.house_robber_scan, "Original Scan": scan.original_scan, "Simple Scan": scan.simple_scan}


# Create your views here.
def index(request, id=""):

    def get_random_poem(only_human_scanned=False):
        if only_human_scanned:
            poem_ids = list(Poem.objects.exclude(scansion="").values_list("id", flat=True))
        else:
            poem_ids = list(Poem.objects.values_list("id", flat=True))
        if poem_ids:
            chosen = choice(poem_ids)
            return Poem.objects.get(id=chosen)
        else:
            tempestuous = """Full fathom five thy father lies:
Of his bones are coral made;
Those are pearls that were his eyes:
Nothing of him that doth fade,
But doth suffer a sea-change
Into something rich and strange;
Sea-nymphs hourly ring his knell:
Hark! now I hear them,--
Ding, dong, Bell."""
            scansion = """u /u / u /u /
/ u / u /u /
/ u / u / u /
/u / u / u /
u u /u u /u
/u /u / u /
/u /u / u /
/ u u / u
/ u /"""

            p = Poem(title="A Sea Dirge",
                        poem=tempestuous,
                        scansion=scansion,
                        poet=Poet.objects.get(last_name="SHAKESPEARE"))
            p.save()
            return p
    def make_dict(scansion):
        """Make dictionary id-ing poem's words by line, word index"""
        if not scansion:
            return ""
        else:
            line_word_dict = {}
            for i, line in enumerate(scansion.splitlines()):
                line_word_dict[i] = {}
                for j, word in enumerate(line.split()):
                    line_word_dict[i][j] = word
            print(line_word_dict)
            return line_word_dict
    
    def make_dict_p(poem):
        p = parse.clean_poem(poem)
        line_word_dict = {}
        for i, line in enumerate(poem.splitlines()):
            line_word_dict[i] = {}
            relevant_words = [word for word in line.split() if parse.clean(word)]
            for j, word in enumerate(relevant_words):
                line_word_dict[i][j] = word
        print(line_word_dict)
        return line_word_dict



    if request.method == "POST":
        pass
    elif request.method == "PUT":
        pass
    else:
        # get chosen poem or random poem
        if id:
            poem = Poem.objects.get(pk=id)
        elif request.user.is_authenticated and request.user.is_promoted():
            poem = get_random_poem()
        else:
            poem = get_random_poem(only_human_scanned=True)

        # get algorithms
        algorithms = Algorithm.objects.all().order_by("-preferred")
        
        # create scansion consisting entirely of "u" to pass to template for React
        blank_slate_to_be = ALGORITHMS[algorithms[0].name](poem.poem)
        almost_blank_slate = blank_slate_to_be.replace(parse.STRESSED, parse.UNSTRESSED)
        blank_slate = almost_blank_slate.replace(parse.UNKNOWN, parse.UNSTRESSED)
        scansions = {"Blank Slate" : {
            "about-algorithm": "",
            "scansion": make_dict(blank_slate)
          }
        }

        for algorithm in algorithms:
            try:
                s = MachineScansion.objects.get(poem=poem, algorithm=algorithm)
            except MachineScansion.DoesNotExist:
                new_scan = ALGORITHMS[algorithm.name](poem.poem)
                s = MachineScansion(poem=poem, scansion=new_scan, algorithm=algorithm)
                s.save()
            scansions[algorithm.name] = {
                    "about-algorithm": algorithm.about, 
                    "scansion": make_dict(s.scansion)
            }
                
        ctxt = {
            "poem": {
                "title" : poem.title,
                "poem": poem.poem,
                "poem_dict": make_dict_p(poem.poem),
                "authoritative": make_dict(poem.scansion),
                "poet": poem.poet.last_name
            }, 
            "scansions": scansions
        }

        return render(request, "scansion/index.html", {
            "ctxt" : ctxt
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            print("Logging in successfully")
            return HttpResponseRedirect(reverse("index"))
        else:
            print("Can't log in")
            return render(request, "scansion/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "scansion/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "scansion/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "scansion/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "scansion/register.html")


def about(request):
    return render(request, "scansion/about.html")

def choose_poem(request):
    human_list = Poem.objects.exclude(scansion="").order_by("poet")
    computer_list = Poem.objects.filter(scansion="").order_by("poet")
    return render(request, "scansion/choose_poem.html", {"human_list": human_list, "computer_list": computer_list})

def rescan_poem(request, id):
    poem = Poem.objects.get(pk=id)
    algorithms = Algorithm.objects.all()
    scansions = []
    for algorithm in algorithms:
        new_scan = ALGORITHMS[algorithm.name](poem.poem)
        try:
            s = MachineScansion.objects.get(poem=poem, algorithm=algorithm)
            s.scasion = new_scan
            s.save()
            scansions.append(s)
        except MachineScansion.DoesNotExist:
            s = MachineScansion(poem=poem, scansion=new_scan, algorithm=algorithm)
            s.save()
            scansions.append(s)
    return render(request, "scansion/index.html", {"poem": poem, "algorithms": algorithms, "scansions": scansions})

@staff_member_required
def rescan_all(request):
    poems = Poem.objects.all()
    algorithms = Algorithm.objects.all()
    for poem in poems:
        for algorithm in algorithms:
            new_scan = ALGORITHMS[algorithm.name](poem.poem)
        try:
            s = MachineScansion.objects.get(poem=poem, algorithm=algorithm)
            s.scansion = new_scan
            s.save()
        except MachineScansion.DoesNotExist:
            s = MachineScansion(poem=poem, scansion=new_scan, algorithm=algorithm)
            s.save()
    return HttpResponseRedirect(reverse("index"))
                
