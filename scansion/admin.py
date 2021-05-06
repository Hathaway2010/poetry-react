from django.contrib import admin
from .models import User, Word, StressPattern, Poem, Poet, Algorithm, HumanScansion, MachineScansion

# Register your models here.
admin.site.register(User)
admin.site.register(Word)
admin.site.register(StressPattern)
admin.site.register(Poem)
admin.site.register(Poet)
admin.site.register(Algorithm)
admin.site.register(HumanScansion)
admin.site.register(MachineScansion)
