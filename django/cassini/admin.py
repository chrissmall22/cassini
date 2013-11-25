from django.contrib import admin
from cassini.models import MacDB, Network, Project, User, Nac_state, Nac_network

admin.site.register(MacDB)
admin.site.register(Network)
admin.site.register(Project)
admin.site.register(User)

admin.site.register(Nac_state)
admin.site.register(Nac_network)
