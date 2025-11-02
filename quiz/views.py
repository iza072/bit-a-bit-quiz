from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import F, Max
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import json
import random

try:
    from google import genai
    from google.genai.errors import APIError 
    
    from usuarios.models import Perfil 
except ImportError:
    
    genai = None
    APIError = Exception
    Perfil = None


# Importações do Aplicativo Quiz
from .models import Pergunta, Resposta, DIFICULDADE_CHOICES, Pontuacao
from .serializers import PerguntaSerializer, PontuacaoSerializer
from django.db import models # Necessário para models.Max


# INICIALIZAÇÃO GLOBAL DA CHAVE GEMINI

gemini_client = None
if settings.GEMINI_API_KEY and genai:
    try:
        gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY) 
    except Exception as e:
        print(f"Erro ao inicializar o cliente Gemini: {e}")


# prioridade (usuario) se nao da erro CHATBOT API (RESTRITO A ASSINANTES)

@require_POST
@login_required
def chatbot_responder(request):
    """
    Endpoint da API para o Chatbot BitBot.
    RESTRITO: Apenas para usuários logados E assinantes.
    """
    if gemini_client is None: 
        return JsonResponse({'error': 'Serviço de IA temporariamente indisponível.'}, status=503)

    # CHECAGEM DE ASSINATURA (RESTRIÇÃO DE ACESSO)
    try:
        if not request.user.perfil.is_assinante:
            return JsonResponse({
                'error': 'Acesso negado. O BitBot é um recurso exclusivo para assinantes.'
            }, status=403)
    except Exception: # Captura Perfil.DoesNotExist ou attributeError
        return JsonResponse({
            'error': 'Erro no perfil do usuário. Acesso negado.'
        }, status=403)
        
    # Processamento da Pergunta
    try:
        data = json.loads(request.body)
        pergunta = data.get('pergunta', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Requisição inválida.'}, status=400)

    if not pergunta:
        return JsonResponse({'resposta': 'Por favor, digite sua pergunta sobre T.I. ou a plataforma.'})

    # interaçao com a api do Gemini
    try:
        system_instruction = (
            "Você é o BitBot, um assistente de inteligência artificial focado em Tecnologia da Informação. "
            "Suas respostas devem ser claras, diretas e úteis para quem estuda T.I. "
            "Responda a pergunta do usuário abaixo. Seja conciso."
        )
        
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=pergunta,
            config={"system_instruction": system_instruction}
        )
        
        resposta_bot = response.text
        return JsonResponse({'resposta': resposta_bot})

    except APIError as e:
        print(f"Erro na API Gemini: {e}")
        return JsonResponse({'error': 'Erro de comunicação com o serviço de IA. Tente mais tarde.'}, status=500)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return JsonResponse({'error': 'Ocorreu um erro interno. Tente novamente.'}, status=500)



#  VIEWS DE TEMPLATE (Renderizam HTML)
@login_required 
def pagina_perguntas_facil(request):
    return render(request, 'perguntas/facil.html')

@login_required
def pagina_perguntas_media(request):
    return render(request, 'perguntas/media.html')

@login_required
def pagina_perguntas_dificil(request):
    return render(request, 'perguntas/dificil.html')
    
@login_required 
def pagina_ranking(request):
    """Renderiza a página HTML do Ranking Global."""
    return render(request, 'ranking.html')

@login_required 
def pagina_chatbot_premium(request):
    """
    Renderiza a página dedicada do Chatbot Premium.
    Bloqueia o acesso de não-assinantes aqui no Django.
    """
    # Checagem de Assinatura
    is_assinante = False
    try:
        if request.user.perfil.is_assinante:
             is_assinante = True
    except:
        pass # Se não tiver perfil premium ou erro, is_assinante fica False

    if not is_assinante:
        # O nome da URL da página principal é 'principal'
        return redirect('principal') 

    # Se for assinante, renderiza a página
    return render(request, 'chatbot.html') 


#  VIEWS DA API (JSON)
@api_view(['POST']) 
@login_required 
def salvar_pontuacao_final(request):
    """
    Endpoint: /api/quiz/salvar_pontuacao/
    Recebe a pontuação total final de um quiz concluído e a salva.
    """
    pontos_totais = request.data.get('pontuacao')
    dificuldade_char = request.data.get('dificuldade', '').upper()
    
    if pontos_totais is None or dificuldade_char not in ['F', 'M', 'D']:
        return Response(
            {"detail": "Pontuação e dificuldade válidas são obrigatórias."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        Pontuacao.objects.create(
            usuario=request.user,
            pontos_totais=int(pontos_totais),
            dificuldade=dificuldade_char
        )
        
        return Response(
            {"detail": "Pontuação final registrada com sucesso."}, 
            status=status.HTTP_201_CREATED
        )
            
    except Exception as e:
        print(f"Erro ao salvar pontuação: {e}")
        return Response({"detail": "Erro interno ao registrar a pontuação."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def obter_perguntas_quiz(request, dificuldade):
    """
    Endpoint: /api/quiz/{dificuldade}/
    Retorna 5 perguntas aleatórias de uma dificuldade específica ('F', 'M' ou 'D').
    """
    dificuldade_char = dificuldade.upper()

    if dificuldade_char not in ['F', 'M', 'D']:
        return Response(
            {"detail": "Dificuldade inválida. Use F, M ou D."},
            status=status.HTTP_400_BAD_REQUEST
        )

    perguntas_queryset = Pergunta.objects.filter(dificuldade=dificuldade_char).order_by('?')[:5]
    
    if not perguntas_queryset.exists():
        return Response(
            {"detail": f"Nenhuma pergunta encontrada para a dificuldade {dificuldade_char}."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = PerguntaSerializer(perguntas_queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@login_required
def verificar_resposta(request):
    """
    Endpoint: /api/quiz/verificar/
    Recebe o ID da resposta escolhida via POST e verifica se está correta.
    """
    resposta_id = request.data.get('resposta_id') 
    
    if not resposta_id:
        return Response(
            {"detail": "ID da resposta é obrigatório."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
        
    try:
        resposta = Resposta.objects.select_related('pergunta').get(pk=resposta_id)
        
        correta = resposta.is_correta
        pontos = 0
        
        if correta:
            dificuldade = resposta.pergunta.dificuldade
            if dificuldade == 'F':
                pontos = 10
            elif dificuldade == 'M':
                pontos = 25
            elif dificuldade == 'D':
                pontos = 50
        
        return Response({'correta': correta, 'pontos': pontos}, status=status.HTTP_200_OK)
            
    except Resposta.DoesNotExist:
        return Response({"detail": "Resposta não encontrada."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Erro ao verificar resposta: {e}")
        return Response({"detail": "Erro interno ao processar a resposta."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@login_required 
def obter_ranking_top10(request):
    """
    Endpoint: /api/quiz/ranking/
    Retorna as 10 maiores pontuações já registradas no sistema.
    """
    ranking_data = Pontuacao.objects.select_related('usuario').values('usuario__username').annotate(
        maior_pontuacao=models.Max('pontos_totais')
    ).order_by('-maior_pontuacao')[:10]

    data = [
        {
            'username': item['usuario__username'],
            'pontuacao': item['maior_pontuacao']
        }
        for item in ranking_data
    ]
    
    return Response(data, status=status.HTTP_200_OK)


#  VIEW DE GERAÇÃO DE PERGUNTAS (IA)

@api_view(['GET'])
@login_required 
def obter_historico_pontuacao(request):
    """
    Endpoint: /api/quiz/historico/
    Retorna o histórico de pontuações do usuário logado.
    """
    historico = Pontuacao.objects.filter(usuario=request.user).order_by('-data_conclusao')
    
    if not historico.exists():
        return Response(
            {"detail": "Nenhum registro de pontuação encontrado para este usuário."},
            status=status.HTTP_200_OK
        )
        
    serializer = PontuacaoSerializer(historico, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@login_required
def gerar_e_salvar_perguntas(request, dificuldade_char): 
    """
    Endpoint: /api/quiz/gerar/{dificuldade_char}/
    Usa a API Gemini para gerar 5 perguntas e salvar no banco de dados.
    """
    dificuldade_char = dificuldade_char.upper()
    dificuldade_nome = dict(DIFICULDADE_CHOICES).get(dificuldade_char, 'Fácil')
    
    # Checagens de segurança e disponibilidade da propria IA 
    if gemini_client is None:
        return Response({"detail": "API Key do Gemini não está configurada ou indisponível."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    if dificuldade_char not in ['F', 'M', 'D']:
        return Response(
            {"detail": "Dificuldade inválida para geração. Use F, M ou D."},
            status=status.HTTP_400_BAD_REQUEST
        )

    prompt = f"""
    Gere 5 perguntas de múltipla escolha sobre Tecnologia da Informação (TI) de dificuldade {dificuldade_nome}.
    Para cada pergunta, gere exatamente 4 opções de resposta.
    Apenas uma opção deve ser a correta.
    O formato da saída DEVE ser estritamente um array JSON, onde cada objeto é uma pergunta.
    
    [
      {{
        "texto": "Pergunta 1...",
        "respostas": [
          {{"texto": "Resposta A", "correta": false}},
          {{"texto": "Resposta B", "correta": true}},
          {{"texto": "Resposta C", "correta": false}},
          {{"texto": "Resposta D", "correta": false}}
        ]
      }},
      ...
    ]
    """

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt,
            config={"response_mime_type": "application/json"} 
        )
        
        perguntas_json = json.loads(response.text)
        
        # LOGICA DE SALTAVEMNTO PARA O BANCO DE DADOS 
        perguntas_salvas = 0
        for item in perguntas_json:
            pergunta = Pergunta.objects.create(
                texto=item['texto'],
                dificuldade=dificuldade_char,
                categoria='Geração IA'
            )
            
            for resp_data in item['respostas']:
                Resposta.objects.create(
                    pergunta=pergunta,
                    texto=resp_data['texto'],
                    is_correta=resp_data['correta']
                )
            perguntas_salvas += 1
            
        return Response(
            {"detail": f"{perguntas_salvas} perguntas de dificuldade {dificuldade_nome} geradas e salvas com sucesso."},
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        print(f"Erro FATAL na geração da IA: {e}") 
        return Response(
            {"detail": f"Erro na geração ou salvamento da IA. Detalhes: {e}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )