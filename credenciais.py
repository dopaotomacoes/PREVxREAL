import os
import logging
import sys
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr, Field, ValidationError
from typing import Optional, Dict, Any

# Configuração de logging profissional:
# - Registra logs em arquivo 'app.log' (append)
# - Mostra logs no console para facilitar desenvolvimento
# - Formato padrão com timestamp, nível e mensagem
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Carrega variáveis de ambiente do arquivo .env para o ambiente do Python
load_dotenv()

class EmailConfig(BaseModel):
    """
    Modelo Pydantic para configuração de email.
    Valida email válido e senha não vazia.
    """
    email: EmailStr
    senha: str = Field(..., min_length=1)

class AppKeysConfig(BaseModel):
    """
    Modelo Pydantic para chaves de API.
    Valida app_key e app_secret como strings não vazias.
    """
    app_key: str = Field(..., min_length=1)
    app_secret: str = Field(..., min_length=1)

class Config:
    """
    Classe estática para carregar e validar configurações do sistema
    a partir das variáveis de ambiente definidas no arquivo .env.
    """

    @staticmethod
    def get_email_config(localidade: str, servico: str) -> Optional[EmailConfig]:
        """
        Retorna configuração de email para localidade e serviço.

        Args:
            localidade (str): Nome da localidade (ex: 'pinheirinho')
            servico (str): Nome do serviço (ex: 'cartao')

        Returns:
            EmailConfig ou None se inválido ou não configurado.
        """
        localidade = localidade.upper()
        servico = servico.upper()
        email_var = f"{localidade}_{servico}_EMAIL"
        senha_var = f"{localidade}_{servico}_SENHA"

        email = os.getenv(email_var)
        senha = os.getenv(senha_var)

        if not email or not senha:
            logging.warning(f"Variáveis de ambiente {email_var} ou {senha_var} não configuradas.")
            return None

        try:
            return EmailConfig(email=email, senha=senha)
        except ValidationError as exc:
            logging.error(f"Validação falhou para {localidade}_{servico}: {exc}")
            return None

    @staticmethod
    def get_app_keys(localidade: str, servico: str) -> Optional[AppKeysConfig]:
        """
        Retorna chaves de API para localidade e serviço.

        Args:
            localidade (str): Nome da localidade
            servico (str): Nome do serviço

        Returns:
            AppKeysConfig ou None se inválido ou não configurado.
        """
        localidade = localidade.upper()
        servico = servico.upper()
        app_key_var = f"{localidade}_{servico}_APP_KEY"
        app_secret_var = f"{localidade}_{servico}_APP_SECRET"

        app_key = os.getenv(app_key_var)
        app_secret = os.getenv(app_secret_var)

        if not app_key or not app_secret:
            logging.warning(f"Variáveis de ambiente {app_key_var} ou {app_secret_var} não configuradas.")
            return None

        try:
            return AppKeysConfig(app_key=app_key, app_secret=app_secret)
        except ValidationError as exc:
            logging.error(f"Validação falhou para {localidade}_{servico}: {exc}")
            return None

    @staticmethod
    def get_imap_config() -> Optional[Dict[str, Any]]:
        """
        Retorna configurações de servidor IMAP.

        Returns:
            Dict com 'servidor' e 'porta' ou None se inválido.
        """
        servidor = os.getenv("SERVIDOR")
        porta = os.getenv("PORTA")

        if not servidor or not porta:
            logging.warning("Variáveis de ambiente SERVIDOR ou PORTA não configuradas.")
            return None

        try:
            return {
                "servidor": servidor,
                "porta": int(porta)
            }
        except ValueError:
            logging.error("Valor inválido para PORTA; deve ser inteiro.")
            return None

    @staticmethod
    def get_azure_config() -> Optional[Dict[str, str]]:
        """
        Retorna configurações para integração com Azure.

        Returns:
            Dict com chaves e endpoint ou None se incompleto.
        """
        key1 = os.getenv("KEY1")
        key2 = os.getenv("KEY2")
        regiao = os.getenv("REGIAO")
        endpoint = os.getenv("ENDPOINT")

        if not all([key1, key2, regiao, endpoint]):
            logging.warning("Variáveis de ambiente Azure incompletas.")
            return None

        return {
            "key1": key1,
            "key2": key2,
            "regiao": regiao,
            "endpoint": endpoint,
        }

    @staticmethod
    def get_openai_config() -> Optional[Dict[str, str]]:
        """
        Retorna configurações para OpenAI.

        Returns:
            Dict com endpoint, modelo, deployment, subscription_key e api_version ou None.
        """
        endpoint = os.getenv("ENDPOINT_OPENAI")
        model_name = os.getenv("MODEL_NAME")
        deployment = os.getenv("DEPLOYMENT")
        subscription_key = os.getenv("SUBSCRIPTION_KEY")
        api_version = os.getenv("API_VERSION")

        if not all([endpoint, model_name, deployment, subscription_key, api_version]):
            logging.warning("Variáveis de ambiente OpenAI incompletas.")
            return None

        return {
            "endpoint_openai": endpoint,
            "model_name": model_name,
            "deployment": deployment,
            "subscription_key": subscription_key,
            "api_version": api_version,
        }

    @staticmethod
    def get_paths() -> Optional[Dict[str, str]]:
        """
        Retorna caminhos importantes do sistema (ex: PATH_BOLETO).

        Returns:
            Dict com paths ou None se ausente.
        """
        path_boleto = os.getenv("PATH_BOLETO")
        if not path_boleto:
            logging.warning("Variável de ambiente PATH_BOLETO não configurada.")
            return None
        return {"path_boleto": path_boleto}
