
from Services.config_manager import ConfigManager
from Services.sftp_service import SftpService, SftpServiceOptions
from DataModel.sftp_client_config import SftpClientConfig

import os
import shutil
import logging
import DataModel.config as Config

# Configurer le logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("C:\Logs\SftpGetFiles.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        # Initialiser le ConfigManager avec le chemin du fichier de configuration
        config_manager = ConfigManager("Data/config.json", Config)
        
        # Charger la configuration
        config = config_manager.load_config()
        
        # Vérifier si la configuration a été chargée correctement
        if not config:
            raise ValueError("La configuration n'a pas pu être chargée. Veuillez vérifier le fichier de configuration.")

        logger.info(f"API URL: {config.api_url}, Timeout: {config.timeout}, Retry Count: {config.retry_count}")

        for client in config.sftp_clients:
            try:
                # Vérifier que tous les champs nécessaires sont présents dans la configuration du client
                if not all([client.name, client.destination_ftp_url, client.remote_file_path, client.local_download_path, client.local_downloaded_file_name]):
                    logging.error(f"Erreur de configuration pour le client {client.name}. Certains champs sont manquants.")
                    continue

                logger.info(f"Traitement du client : {client.name}")
                logger.info(f"Destination FTP URL: {client.destination_ftp_url}, Remote File Path: {client.remote_file_path}, Local Download Path: {client.local_download_path}")

                # Initialiser le service SFTP avec des options génériques
                sftp_options = SftpServiceOptions(
                    host=client.destination_ftp_url,
                    port=client.destination_ftp_port,
                    username=client.login,
                    password=client.password,
                    timeout=config.timeout,
                    retry_count=config.retry_count
                )
                sftp_service = SftpService(sftp_options, logger)

                # Vider le répertoire local de téléchargement avant de télécharger les fichiers
                try:
                    if os.path.exists(client.local_download_path):
                        shutil.rmtree(client.local_download_path)
                    os.makedirs(client.local_download_path)
                except OSError as e:
                    logger.error(f"Erreur lors de la préparation du répertoire local ({client.local_download_path}) : {e}")
                    continue

                # Lister les fichiers dans le répertoire distant SFTP
                remote_files = sftp_service.list_files(client.remote_file_path)

                if not remote_files:
                    logger.warning(f"Aucun fichier trouvé sur le serveur SFTP pour le client {client.name}")
                    continue

                # Télécharger le premier fichier du répertoire distant
                first_remote_file = remote_files[0]
                local_file_path = os.path.join(client.local_download_path, client.local_downloaded_file_name)
                try:
                    sftp_service.download_file(os.path.join(client.remote_file_path, first_remote_file), local_file_path)
                except Exception as e:
                    logger.error(f"Erreur lors du téléchargement du fichier {first_remote_file} pour le client {client.name} : {e}")
                    continue
                
                # Supprimer tous les fichiers dans le répertoire distant SFTP en une seule connexion
                try:
                    sftp_service.delete_files([os.path.join(client.remote_file_path, remote_file) for remote_file in remote_files])
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression des fichiers pour le client {client.name} : {e}")
                    continue

                logger.info(f"Le fichier {first_remote_file} a été téléchargé et renommé en {client.local_downloaded_file_name}, tous les autres fichiers ont été supprimés du serveur SFTP.")
            except Exception as e:
                logger.error(f"Une erreur inattendue s'est produite pour le client {client.name} : {e}")

    except Exception as e:
        logger.critical(f"Une erreur inattendue s'est produite : {e}")