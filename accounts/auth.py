from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailBackend(ModelBackend):
    """
    Backend de autenticação personalizado que permite aos usuários fazer login usando o e-mail.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Tenta autenticar usando o e-mail como nome de usuário
            user = User.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            # Retorna None se o usuário não existir
            return None
        except User.MultipleObjectsReturned:
            # Se houver múltiplos usuários com o mesmo e-mail, usa o primeiro
            user = User.objects.filter(Q(username=username) | Q(email=username)).first()
            if user.check_password(password):
                return user
        return None
