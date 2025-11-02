from django.urls import path
from . import views

urlpatterns = [
   
    # ROTAS DE TEMPLATE (PÁGINAS HTML)
    
    path('quiz/facil/', views.pagina_perguntas_facil, name='perguntas_facil'),
    path('quiz/media/', views.pagina_perguntas_media, name='perguntas_media'),
    path('quiz/dificil/', views.pagina_perguntas_dificil, name='perguntas_dificil'),
    path('ranking/', views.pagina_ranking, name='ranking'),
    # URL DO CHATBOT (O nome 'chatbot_page' deve ser usado no principal.html)
    path('chatbot/premium/', views.pagina_chatbot_premium, name='chatbot_page'),
    
    
    # ROTAS DE API (Endpoints JSON) APAGADo
    

    # Rotas Estáticas (POST ou GET)
    path('api/quiz/verificar/', views.verificar_resposta, name='api_verificar_resposta'),
    path('api/quiz/salvar_pontuacao/', views.salvar_pontuacao_final, name='api_salvar_pontuacao'),
    path('api/quiz/historico/', views.obter_historico_pontuacao, name='api_historico_pontuacao'),
    path('api/quiz/ranking/', views.obter_ranking_top10, name='api_ranking_top10'), 
    path('api/chatbot/responder/', views.chatbot_responder, name='api_chatbot_responder'),
    
    # ROTAS  GENERICAS (Devem vir por último) PARA NAO DAR ERRO 
    path('api/quiz/gerar/<str:dificuldade_char>/', views.gerar_e_salvar_perguntas, name='api_gerar_perguntas_ia'),
    path('api/quiz/<str:dificuldade>/', views.obter_perguntas_quiz, name='api_obter_perguntas'),
]