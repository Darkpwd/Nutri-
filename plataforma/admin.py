from django.contrib import admin
from .models import Pacientes, DadosPacientes, Refeicao, Opcao

admin.site.register(Pacientes)
admin.site.register(DadosPacientes)
admin.site.register(Refeicao)
admin.site.register(Opcao)
