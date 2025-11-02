from django.db import models
from django.contrib.auth.models import User

class Perfil(models.Model):
    """
    Modelo de perfil estendido, conectado ao User padrão do Django.
    Contém campos específicos do Bit a Bit (assinatura, pontuação, foto).
    """
    #  Conexão com o modelo User.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # CAMPO DE ASSINATURA
    is_assinante = models.BooleanField(default=False)
    
    # CAMPO DE PONTUAÇÃO
    pontuacao_total = models.IntegerField(default=0)
    
    #  CAMPO DE FOTO DE PERFIL 
    # 'fotos_perfil/' e o subdiretório dentro de MEDIA_ROOT
    foto_perfil = models.ImageField(
        upload_to='fotos_perfil/', 
        null=True, 
        blank=True,
        #!!!crias arquivo 'default.png' dentro da pasta 'media/fotos_perfil/'
        default='fotos_perfil/default.png' 
    )
    
   
    def __str__(self):
        return f'Perfil de {self.user.username}'