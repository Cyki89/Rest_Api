import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import MlModel
from .helpers import get_filepath

@receiver(post_delete, sender=MlModel)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    '''
    Delete file from filesystem
    when corresponding MlModel's object is deleted.
    '''
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(pre_save, sender=MlModel)
def auto_change_file_on_update(sender, instance, **kwargs):
    '''
    Delete old file from filesystem
    when MlModel's file was replaced
    or
    change file endopoint
    when model parameters was updated.
    '''
    if not instance.pk:
        return False

    try:
        old_file = MlModel.objects.get(pk=instance.pk).file
    except MlModel.DoesNotExist:
        return False

    # delete old file
    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)

    # change file path when nessesary
    elif not new_file == get_filepath(instance):
        os.rename(f'{new_file}', f'{get_filepath(instance)}')
        instance.file = get_filepath(instance)
