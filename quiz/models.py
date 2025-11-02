from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model # modelo de usuário ativo no projeto
User = get_user_model()

# Opções de Dificuldade do quiz
DIFICULDADE_CHOICES = (
    ('F', 'Fácil'),
    ('M', 'Médio'),
    ('D', 'Difícil'),
)

class Pergunta(models.Model):
    """Representa uma questão do quiz."""
    texto = models.TextField(verbose_name="Texto da Pergunta")
    
    dificuldade = models.CharField(
        max_length=1,
        choices=DIFICULDADE_CHOICES,
        default='F',
        verbose_name="Dificuldade"
    )
    
    
    categoria = models.CharField(max_length=100, default='Geral', verbose_name="Categoria")
    
    tempo_limite = models.IntegerField(
        default=30, 
        help_text="Tempo em segundos para responder (ex: 30s)",
        verbose_name="Tempo Limite"
    )

    def __str__(self):
        return f"[{self.dificuldade}] {self.texto[:50]}..."

    class Meta:
        verbose_name = "Pergunta"
        verbose_name_plural = "Perguntas"


class Resposta(models.Model):
    """Representa uma das opções de resposta para uma Pergunta."""
    pergunta = models.ForeignKey(
        Pergunta, 
        related_name='respostas', 
        on_delete=models.CASCADE,
        verbose_name="Pergunta Relacionada"
    )
    texto = models.CharField(max_length=255, verbose_name="Texto da Resposta")
    is_correta = models.BooleanField(default=False, verbose_name="É a Resposta Correta?")

    def __str__(self):
        return f"Resposta para {self.pergunta.id}: {self.texto[:30]}..."

    class Meta:
        verbose_name = "Resposta"
        verbose_name_plural = "Respostas"

   #nova classe para registrar a pontuaçao dos usuarios 

class Pontuacao(models.Model):
    """
    Registra a pontuação de um usuário em um quiz concluído.
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pontuacoes')
    pontos_totais = models.IntegerField(default=0)
    data_conclusao = models.DateTimeField(auto_now_add=True)
    dificuldade = models.CharField(max_length=1, choices=DIFICULDADE_CHOICES, default='F')

    def __str__(self):
        return f'{self.usuario.username} - {self.pontos_totais} pts ({self.get_dificuldade_display()})'

    class Meta:
        verbose_name = "Pontuação do Usuário"
        verbose_name_plural = "Pontuações dos Usuários"