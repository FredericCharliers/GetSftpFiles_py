import json 
from DataModel.sftp_client_config import SftpClientConfig
from pydantic import BaseModel
from typing import Any, List

class Config(BaseModel):
    api_url: str
    timeout: int
    retry_count: int
    sftp_clients: List[SftpClientConfig]    
