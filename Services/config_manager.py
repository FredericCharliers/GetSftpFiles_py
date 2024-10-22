import json
from pydantic import BaseModel, ValidationError
from typing import Any, Type

class ConfigManager:
    config = None

    def __init__(self, file_path:str, config_class: Type):
         """
         Initialise le ConfigManager avec le chemin du fichier de configuration et l'objet Config.

         Args:
            file_path (str): Chemin vers le fichier de configuration.
            config (Config): Instance de la classe Config pour stocker les valeurs de configuration.
         """
         self.file_path = file_path        
         self.config_class = config_class 
    
    def load_config(self, reload:bool = False):
        """
        Charge la configuration depuis le fichier JSON et met à jour l'objet Config.

        Returns:
            Config: Un objet Config contenant les paramètres mis à jour.
        """
        try:
            if (ConfigManager.config is None):
                with open(self.file_path, 'r') as config_file:
                    config_data: Any = json.load(config_file)
                ConfigManager.config = self.config_class(**config_data)
                return ConfigManager.config
            else:
                return ConfigManager.config
        except FileNotFoundError:
            print(f"Erreur : Le fichier de configuration '{self.file_path}' est introuvable.")
        except json.JSONDecodeError:
            print(f"Erreur : Le fichier de configuration '{self.file_name}' n''est pas au bon format.")
        except ValidationError as e:
            print(f"Erreur de validation de la configuration {e}")