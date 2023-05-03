from pydantic import BaseSettings

class TwilioSettings(BaseSettings):
    account_sid: str
    auth_token: str
    to_phone_number: str
    from_phone_number: str
    
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    database_instance_connection_name: str

    class Config:
        env_file = ".env"

settings = TwilioSettings()