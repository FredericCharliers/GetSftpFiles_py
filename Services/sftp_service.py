import paramiko
import logging
import time
import os

from pydantic import BaseModel
from DataModel.sftp_client_config import SftpClientConfig
from typing import List

class SftpServiceOptions:
    def __init__(self, host: str, port: int, username: str, password: str, timeout: int, retry_count: int):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.retry_count = retry_count

class SftpService:
    def __init__(self, options: SftpServiceOptions, logger: logging.Logger):
        self.options = options
        self.logger = logger

    def list_files(self, remote_directory: str) -> List[str]:
        """
        Liste les fichiers dans un répertoire distant sur le serveur SFTP.

        Args:
            remote_directory (str): Chemin du répertoire distant sur le serveur SFTP.

        Returns:
            List[str]: Liste des fichiers présents dans le répertoire distant.
        """
        attempt = 0
        while attempt < self.options.retry_count:
            try:
                transport = paramiko.Transport((self.options.host, self.options.port))
                transport.connect(username=self.options.username, password=self.options.password, timeout=self.options.timeout)
                sftp = paramiko.SFTPClient.from_transport(transport)

                files = sftp.listdir(remote_directory)

                sftp.close()
                transport.close()

                self.logger.info(f"Liste des fichiers récupérés depuis {remote_directory} : {files}")
                return files
            except (paramiko.SSHException, FileNotFoundError) as e:
                attempt += 1
                self.logger.error(f"Erreur lors de la liste des fichiers sur le serveur SFTP (tentative {attempt}/{self.options.retry_count}) : {e}")
                time.sleep(2)  # Attendre avant de réessayer
                if attempt >= self.options.retry_count:
                    self.logger.error(f"Échec après {self.options.retry_count} tentatives. Impossible de lister les fichiers.")
                    return []

    def download_file(self, remote_file_path: str, local_file_path: str):
        """
        Télécharge un fichier depuis le serveur SFTP vers un chemin local.

        Args:
            remote_file_path (str): Chemin du fichier distant sur le serveur SFTP.
            local_file_path (str): Chemin local où le fichier sera téléchargé.
        """
        attempt = 0
        while attempt < self.options.retry_count:
            try:
                transport = paramiko.Transport((self.options.host, self.options.port))
                transport.connect(username=self.options.username, password=self.options.password, timeout=self.options.timeout)
                sftp = paramiko.SFTPClient.from_transport(transport)

                sftp.get(remote_file_path, local_file_path)

                sftp.close()
                transport.close()
                self.logger.info(f"Téléchargement réussi : {remote_file_path} -> {local_file_path}")
                return
            except (paramiko.SSHException, FileNotFoundError) as e:
                attempt += 1
                self.logger.error(f"Erreur lors du téléchargement du fichier depuis le serveur SFTP (tentative {attempt}/{self.options.retry_count}) : {e}")
                time.sleep(2)  # Attendre avant de réessayer
                if attempt >= self.options.retry_count:
                    self.logger.error(f"Échec après {self.options.retry_count} tentatives. Le téléchargement a échoué.")

    def delete_files(self, remote_file_paths: List[str]):
        """
        Supprime une liste de fichiers sur le serveur SFTP.

        Args:
            remote_file_paths (List[str]): Liste des chemins des fichiers distants à supprimer.
        """
        attempt = 0
        while attempt < self.options.retry_count:
            try:
                transport = paramiko.Transport((self.options.host, self.options.port))
                transport.connect(username=self.options.username, password=self.options.password, timeout=self.options.timeout)
                sftp = paramiko.SFTPClient.from_transport(transport)

                for remote_file_path in remote_file_paths:
                    try:
                        sftp.remove(remote_file_path)
                        self.logger.info(f"Fichier supprimé : {remote_file_path}")
                    except FileNotFoundError:
                        self.logger.warning(f"Le fichier n'a pas été trouvé et ne peut être supprimé : {remote_file_path}")

                sftp.close()
                transport.close()
                return
            except (paramiko.SSHException) as e:
                attempt += 1
                self.logger.error(f"Erreur lors de la suppression des fichiers sur le serveur SFTP (tentative {attempt}/{self.options.retry_count}) : {e}")
                time.sleep(2)  # Attendre avant de réessayer
                if attempt >= self.options.retry_count:
                    self.logger.error(f"Échec après {self.options.retry_count} tentatives. La suppression des fichiers a échoué.")

