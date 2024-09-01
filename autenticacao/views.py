from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .utils import password_is_valid, email_html
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages, auth
import os 
from django.conf import settings
from .models import Ativacao
from hashlib import sha256



def cadastro(request):
    if request.method == 'GET':
        
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'cadastro.html')
    
    elif request.method == 'POST':
        usuario = request.POST.get('usuario')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmacao_senha = request.POST.get('confirmar_senha')    
        
        if not password_is_valid(request, senha, confirmacao_senha):
            return redirect('/auth/cadastro')
        
        try:
            # Salvar dados do cadastro em um banco de dados
            user = User.objects.create_user(
                username=usuario,
                email=email,
                password=senha,
                is_active = False)
            
            messages.add_message(request, constants.SUCCESS, 'Cadastro realizado com sucesso!')
            user.save()
            token = sha256(f"{usuario}{email}".encode()).hexdigest()
        
            # Salvar token de ativação em um banco de dados
            ativacao = Ativacao(token=token, user=user)
            
            ativacao.save()
            
            
            path_template = os.path.join(settings.BASE_DIR, 'autenticacao/templates/emails/cadastro_confirmado.html')
            email_html(path_template, 'Cadastro confirmado', [email,], username=usuario, link_ativacao=f"127.0.0.1:8000/auth/ativar_conta/{token}")
            
        except User.DoesNotExist:
            messages.add_message(request, constants.ERROR, 'Error interno do sistema!')
            return HttpResponse('Usuário já existe!', status=400)    
        
        return redirect('/auth/logar')
        


def logar(request):
    if request.method == "GET":
        
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'login.html')
    
    elif request.method == "POST":
        usuario = request.POST.get('usuario')
        senha = request.POST.get('senha')
        
        
        usuario = auth.authenticate(username=usuario, password=senha)
        
        if usuario is not None:
            auth.login(request, usuario)
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('pacientes')
        else:
            messages.error(request, 'Erro ao logar, credenciais inválidas!')
            return redirect('logar')
        

def sair(request):
    auth.logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('logar')


def ativar_conta(request, token):
    token = get_object_or_404(Ativacao, token=token)
    if token.ativo:
        messages.add_message(request, constants.WARNING, 'Essa token já foi usado')
        return redirect('/auth/logar')
    user = User.objects.get(username=token.user.username)
    
    user.is_active = True
    user.save()
    token.ativo = True
    token.save()
    messages.add_message(request, constants.SUCCESS, 'Conta ativa com sucesso')
    return redirect('/auth/logar')