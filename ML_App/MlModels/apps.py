from django.apps import AppConfig


class MlmodelsConfig(AppConfig):
    name = 'MlModels'

    def ready(self):
        import MlModels.signals
