from django.shortcuts import HttpResponseRedirect, render
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
# https://www.kite.com/python/docs/django.contrib.admindocs.views.staff_member_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Max
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.template.defaulttags import register

import random
import json
from random import choice

from .models import User, Word, StressPattern, Poet, Poem, Algorithm, HumanScansion, MachineScansion
from . import scan
from . import parse

ALGORITHMS = {"House Robber Scan": scan.house_robber_scan, "Original Scan": scan.original_scan, "Simple Scan": scan.simple_scan}

def generate_context(poem, promoted):
       # get algorithms
        algorithms = Algorithm.objects.all().order_by("-preferred")
        
        # create scansion consisting entirely of "u" to pass to template for React
        blank_slate_to_be = ALGORITHMS[algorithms[0].name](poem.poem)
        almost_blank_slate = blank_slate_to_be.replace(parse.STRESSED, parse.UNSTRESSED)
        blank_slate = almost_blank_slate.replace(parse.UNKNOWN, parse.UNSTRESSED)
        scansions = {"Blank Slate" : {
            "about-algorithm": "",
            "scansion": parse.make_dict(blank_slate)
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
                    "about_algorithm": algorithm.about, 
                    "scansion": parse.make_dict(s.scansion)
            }
        
        pts = Poet.objects.all().order_by("last_name")
        if promoted:
            poets = [poet.last_name for poet in pts]
        else:
            poets = []
            for poet in pts:
                if Poem.objects.filter(poet=poet).exclude(scansion="").exists():
                    poets.append(poet.last_name)

        if poem.title:
            title = poem.title
        else:
            title = poem.first_line()

        ps = Poem.objects.filter(poet=poem.poet)
        poems_dict = {"human_scanned": [], "computer_scanned": []}
        for p in ps:
            if p.title:
                title = p.title
            else:
                title = p.first_line()
            poem_info = [p.pk, title]
            if p.scansion:
                poems_dict["human_scanned"].append(poem_info)
            else:
                poems_dict["computer_scanned"].append(poem_info)
                
        return {
            "poem": {
                "id": poem.pk,
                "title" : title,
                "poem": poem.poem,
                "poem_dict": parse.make_dict_p(poem.poem),
                "authoritative": parse.make_dict(poem.scansion),
                "poet": poem.poet.last_name
            }, 
            "scansions": scansions,
            "poets": poets,
            "poems": poems_dict
        }


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
    
    if request.method == "POST":
        pass
    elif request.method == "PUT":
        data = json.loads(request.body)
        # if the user has proven themselves, write their scansion to the database
        if request.user.is_authenticated and request.user.is_promoted():
            # update poem's scansion in the poem table and mark it human-scanned
            s = parse.make_string(data["scansion"])
            p = Poem.objects.get(pk=data["id"])
            hs = HumanScansion(poem=p, scansion=s, user=request.user)
            hs.save()
            if p.scansion:
                h = HumanScansion.objects.filter(poem=p)
                p.scansion = scan.reconcile(p.scansion, h, data["diffs"])
                p.save()
            else:
                p.scansion = s
                p.save()
            
            
            p.human_scanned = True
            p.save()
            # use record function from scan.py to update popularities of word scansions
            # in Pronunciation instances
            scan.record(p.poem, s)
            return HttpResponse()

        # otherwise, score the user
        elif request.user.is_authenticated:
            u = request.user
            u.score += int(data["score"])
            u.save()
            # promote the user if their score has reached 10 points
            resp_data = {"score": u.score, "promoted": u.is_promoted()}
            return JsonResponse(resp_data)
        else:
            return HttpResponse()
    else:
        # get chosen poem or random poem
        if id:
            poem = Poem.objects.get(pk=id)
        elif request.user.is_authenticated and request.user.is_promoted():
            poem = get_random_poem()
        else:
            poem = get_random_poem(only_human_scanned=True)

       

        return render(request, "scansion/index.html", {
            "ctxt" : generate_context(poem, request.user.is_authenticated and request.user.is_promoted())
    })
def poem(request, id):
    poem = Poem.objects.get(pk=id)
    data = generate_context(poem, request.user.is_authenticated and request.user.is_promoted())
    return JsonResponse(data)

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

def choose_poem(request, poet_name):
    def get_data(poem_qset):
        poem_data_list = []
        for poem in poem_qset:
            if poem.title:
                title = poem.title
            else:
                title = poem.first_line()
            poem_data_list.append([poem.pk, title])
        return poem_data_list
    poet = Poet.objects.get(last_name=poet_name)
    poems = Poem.objects.filter(poet=poet)
    human_queryset = poems.exclude(scansion="").order_by("poet")
    human_list = get_data(human_queryset)
    computer_queryset = poems.filter(scansion="").order_by("poet")
    computer_list = get_data(computer_queryset)
    data = {"human_scanned": human_list, "computer_scanned": computer_list}
    print(data)
    return JsonResponse(data)

def rescan_poem(request, id):
    poem = Poem.objects.get(pk=id)
    algorithms = Algorithm.objects.all().order_by("-preferred")
    blank_slate_to_be = ALGORITHMS[algorithms[0].name](poem.poem)
    almost_blank_slate = blank_slate_to_be.replace(parse.STRESSED, parse.UNSTRESSED)
    blank_slate = almost_blank_slate.replace(parse.UNKNOWN, parse.UNSTRESSED)
    scansions = {
        "Blank Slate" : {
            "about-algorithm": "",
            "scansion": parse.make_dict(blank_slate)
          }
        }    
    for algorithm in algorithms:
        new_scan = ALGORITHMS[algorithm.name](poem.poem)
        try:
            s = MachineScansion.objects.get(poem=poem, algorithm=algorithm)
            s.scasion = new_scan
            s.save()
        except MachineScansion.DoesNotExist:
            s = MachineScansion(poem=poem, scansion=new_scan, algorithm=algorithm)
            s.save()
        scansions[algorithm.name] = {
            "about-algorithm": algorithm.about, 
            "scansion": parse.make_dict(new_scan)
        }
        
        data = {
            "scansions": scansions
        }
    return JsonResponse(data)

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
                
