from django.db import transaction
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from boards.models import Board
from lists.models import List


@receiver(post_save, sender=Board)
def create_default_lists(sender, instance, created, **kwargs):
    """
    Automatically create three default lists ('Todo', 'Doing', 'Done') when a new board is created.
    """
    if created:
        default_titles = [_('Todo'), _('Doing'), _('Done')]
        with transaction.atomic():
            for index, title in enumerate(default_titles, start=1):
                List.objects.create(
                    board=instance,
                    title=title,
                    position=index
                )



