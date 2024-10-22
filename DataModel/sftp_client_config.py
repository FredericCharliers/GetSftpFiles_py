from pydantic import BaseModel

class SftpClientConfig(BaseModel): 
    name: str
    destination_ftp_url: str
    remote_file_path: str
    destination_ftp_port: int
    login: str
    password: str
    local_download_path: str
    local_downloaded_file_name: str
