from time import sleep
from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Connection
from utils import open_file, log
from common.settings.settings import settings

class Banco:
    def __init__(self):
        self.bases = {
            'sabium': settings.SABIUM,
            'dw': settings.DW
        }
        self.max_attempts = settings.MAX_ATTEMPTS
        self.backoff_factor = 2  # Pode parametrizar se quiser

    def _get_connection_string(self, base: str) -> str:
        """Obtém a string de conexão para a base especificada."""
        if base not in self.bases:
            raise ValueError(f"Base de dados '{base}' não configurada.")
        return self.bases[base]

    def _conectar(self, base: str) -> Connection:
        """Estabelece uma conexão com a base, com tentativas e backoff exponencial."""
        conn_str = self._get_connection_string(base)
        last_exception = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                engine = create_engine(conn_str)
                connection = engine.connect()
                log.info(f"[{base.upper()}] Conexão estabelecida.")
                return connection
            except SQLAlchemyError as e:
                last_exception = e
                log.warning(f"[{base.upper()}] Tentativa {attempt}/{self.max_attempts} falhou: {e}")
                sleep(self.backoff_factor ** (attempt - 1))

        log.error(f"Falha ao conectar à base '{base}' após {self.max_attempts} tentativas: {last_exception}")
        raise ConnectionError(f"Falha ao conectar à base '{base}' após {self.max_attempts} tentativas: {last_exception}")

    def consulta(self, params: Dict[str, Any], arquivo: str, base: str) -> Optional[List[Any]]:
        """Executa uma consulta SQL com parâmetros e tentativas de retry."""
        sql = open_file(arquivo)
        last_exception = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                with self._conectar(base) as connection:
                    result = connection.execute(text(sql), params).fetchall()

                if not result:
                    log.warning(f"[{base.upper()}] Consulta vazia para parâmetros: {params}")
                    return None

                log.info(f"[{base.upper()}] Consulta executada com sucesso no arquivo [{arquivo.upper()}]")
                return result

            except SQLAlchemyError as e:
                last_exception = e
                log.warning(f"[{base.upper()}] Tentativa {attempt}/{self.max_attempts} de consulta falhou: {e}")
                sleep(self.backoff_factor ** (attempt - 1))

        log.error(f"Falha ao executar consulta na base '{base}' após {self.max_attempts} tentativas: {last_exception}")
        raise RuntimeError(f"Falha ao executar consulta na base '{base}' após {self.max_attempts} tentativas: {last_exception}")

db = Banco()
