from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models


class UsuarioManager(BaseUserManager):
    """Gerenciador que usa e-mail como identificador de login."""

    use_in_migrations = True

    def _criar(self, email, password, **extra):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        usuario = self.model(email=self.normalize_email(email).lower(), **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._criar(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.update(is_staff=True, is_superuser=True, perfil=Usuario.Perfil.ADMIN)
        return self._criar(email, password, **extra)


class Usuario(AbstractUser):
    """Cliente ou administrador da loja (US01, US02, RN07)."""

    class Perfil(models.TextChoices):
        CLIENTE = "CLIENTE", "Cliente"
        ADMIN = "ADMIN", "Administrador"

    username = None
    first_name = None
    last_name = None
    nome = models.CharField("nome", max_length=120)
    email = models.EmailField("e-mail", unique=True)
    telefone = models.CharField(
        "telefone",
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^[0-9()+\-\s]{8,20}$", "Telefone inválido.")],
    )
    perfil = models.CharField(max_length=10, choices=Perfil.choices, default=Perfil.CLIENTE)
    criado_em = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    objects = UsuarioManager()

    class Meta:
        db_table = "usuario"
        verbose_name = "usuário"
        constraints = [
            models.CheckConstraint(condition=models.Q(perfil__in=["CLIENTE", "ADMIN"]), name="ck_usuario_perfil"),
        ]

    @property
    def is_admin_loja(self) -> bool:
        return self.perfil == self.Perfil.ADMIN

    def __str__(self):
        return f"{self.nome} <{self.email}>"


class Endereco(models.Model):
    """Endereço de entrega do cliente (US03)."""

    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="enderecos")
    apelido = models.CharField(max_length=40, default="Casa")
    logradouro = models.CharField(max_length=150)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=60, blank=True)
    bairro = models.CharField(max_length=80)
    cidade = models.CharField(max_length=80, default="São Paulo")
    cep = models.CharField(max_length=9, validators=[RegexValidator(r"^\d{5}-?\d{3}$", "CEP inválido (00000-000).")])
    principal = models.BooleanField(default=False)

    class Meta:
        db_table = "endereco"
        verbose_name = "endereço"
        ordering = ["-principal", "apelido"]

    def __str__(self):
        comp = f", {self.complemento}" if self.complemento else ""
        return f"{self.logradouro}, {self.numero}{comp} – {self.bairro}, {self.cidade}"
