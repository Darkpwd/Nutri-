from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from .models import Pacientes, DadosPacientes, Refeicao, Opcao
from datetime import datetime 
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url='logar')
def pacientes(request):
    if request.method == 'GET':
        pacientes = Pacientes.objects.filter(nutri=request.user)  # Pacientes da nutri cadastrada.
        return render(request, 'pacientes.html', {'pacientes': pacientes})  # Passando pacientes para o meu template
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        sexo = request.POST.get('sexo')
        idade = request.POST.get('idade')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        
        fields = [nome, sexo, idade, email, telefone]

        if any(len(field.strip()) == 0 for field in fields):
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos!')
            return redirect('pacientes')  
        
        if not idade.isnumeric():
            messages.add_message(request, constants.ERROR, 'A idade deve ser um valor numérico!')
            return redirect('pacientes')  
        if Pacientes.objects.filter(email=email).exists():
            messages.add_message(request, constants.ERROR, 'Já existe um paciente com esse Email!')
            return redirect('pacientes')  
            
        try:
            paciente = Pacientes(  # Salvar no banco de dados.
                nome=nome,
                sexo=sexo,
                idade=int(idade),
                email=email,
                telefone=telefone,
                nutri=request.user  
            )
            paciente.save()
            
            messages.add_message(request, constants.SUCCESS, 'Paciente cadastrado com sucesso!')
            
        except Exception as e:
            messages.add_message(request, constants.ERROR, f'Erro ao cadastrar paciente: {str(e)}')
            
        return redirect('pacientes')  
    
@login_required(login_url='/auth/logar/')
def dados_paciente_listar(request):
    if request.method == "GET":
        pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'dados_paciente_listar.html', {'pacientes': pacientes})
    

@login_required(login_url='/auth/logar/')
def dados_paciente(request, id):
    try:
        paciente = get_object_or_404(Pacientes, id=id)

        if paciente.nutri != request.user:
            messages.add_message(request, constants.ERROR, 'Esse paciente não é seu!')
            return redirect('/dados_paciente', id=id)  
        
        if request.method == "GET":
            dados_pacientes = DadosPacientes.objects.filter(paciente=paciente)
            return render(request, 'dados_pacientes.html', {'paciente': paciente, 'dados_pacientes': dados_pacientes})

        elif request.method == "POST":
            peso = request.POST.get('peso', '').strip()
            altura = request.POST.get('altura', '').strip()
            gordura = request.POST.get('gordura', '').strip()
            musculo = request.POST.get('musculo', '').strip()
            hdl = request.POST.get('hdl', '').strip()
            ldl = request.POST.get('ldl', '').strip()
            colesterol_total = request.POST.get('ctotal', '').strip()
            triglicerideos = request.POST.get('trigliceridos', '').strip()

            if not all([peso, altura, gordura, musculo, hdl, ldl, colesterol_total, triglicerideos]):
                messages.add_message(request, constants.ERROR, 'Preencha todos os campos!')
                return redirect('/dados_paciente', id=id)

            try:
                peso = float(peso)
                altura = float(altura)
                gordura = int(gordura)
                musculo = int(musculo)
                hdl = int(hdl)
                ldl = int(ldl)
                colesterol_total = int(colesterol_total)
                triglicerideos = int(triglicerideos)

                paciente_dados = DadosPacientes(
                    paciente=paciente,
                    data=datetime.now(),
                    peso=peso,
                    altura=altura,
                    gordura=gordura,  
                    musculo=musculo,
                    hdl=hdl,
                    ldl=ldl,
                    colesterol_total=colesterol_total,
                    trigliceridos=triglicerideos
                )
                paciente_dados.save()

                messages.add_message(request, constants.SUCCESS, 'Dados do paciente cadastrados com sucesso!')
                return redirect('/dados_paciente', id=id)
            
            except ValueError as ve:
                messages.add_message(request, constants.ERROR, f'Erro de conversão: {str(ve)}')
                return redirect('/dados_paciente', id=id)

    except Http404:
        return HttpResponse('Paciente não encontrado!', status=404)
    except Exception as e:
        return HttpResponse(f'Erro ao buscar paciente: {str(e)}', status=500)



@login_required(login_url='/auth/logar/')
@csrf_exempt
def grafico_peso(request, id):
    paciente = Pacientes.objects.get(id=id)
    dados = DadosPacientes.objects.filter(paciente=paciente).order_by("data")
    
    pesos = [dado.peso for dado in dados]
    labels = list(range(len(pesos)))
    data = {'peso': pesos,
            'labels': labels}
    return JsonResponse(data)

def plano_alimentar_listar(request, id=None):
    if request.method == "GET":
        if id:
            pacientes = Pacientes.objects.filter(id=id, nutri=request.user)
        else:
            pacientes = Pacientes.objects.filter(nutri=request.user)
        return render(request, 'plano_alimentar_listar.html', {'pacientes': pacientes,})

    
def plano_alimentar(request, id):
    paciente = get_object_or_404(Pacientes, id=id)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('plano_alimentar_listar/')

    if request.method == "GET":
        r1 = Refeicao.objects.filter(paciente=paciente).order_by("horario")
        opaco = Opcao.objects.all()
        return render(request, 'plano_alimentar.html', {'paciente': paciente, 'refeicao':r1, 'opcao':opaco})
        
        
def refeicao(request, id_paciente):
    paciente = get_object_or_404(Pacientes, id=id_paciente)
    if not paciente.nutri == request.user:
        messages.add_message(request, constants.ERROR, 'Esse paciente não é seu')
        return redirect('dados_paciente/')

    if request.method == "POST":
        titulo = request.POST.get('titulo')
        horario = request.POST.get('horario')
        carboidratos = request.POST.get('carboidratos')
        proteinas = request.POST.get('proteinas')
        gorduras = request.POST.get('gorduras')

        r1 = Refeicao(
            paciente=paciente,
            titulo=titulo,
            horario=horario,
            carboidratos=carboidratos,
            proteinas=proteinas,
            gorduras=gorduras
            )

        r1.save()

        messages.add_message(request, constants.SUCCESS, 'Refeição cadastrada')
        return redirect(f'/plano_alimentar/{id_paciente}')


    
def opcao(request, id_paciente):
    if request.method == "POST":
        id_refeicao = request.POST.get('refeicao')
        imagem = request.FILES.get('imagem')
        descricao = request.POST.get("descricao")

        o1 = Opcao(
            refeicao_id=id_refeicao,
            imagem=imagem,
            descricao=descricao
            )

        o1.save()

        messages.add_message(request, constants.SUCCESS, 'Opção cadastrada!')
        return redirect(f'/plano_alimentar/{id_paciente}')
    

    
    
    