from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = _('Accounts')

    def ready(self):
        # Import signals to ensure they are registered when Django starts
        import accounts.signals
