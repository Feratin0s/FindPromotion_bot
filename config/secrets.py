import json
import os
from pathlib import Path

def load_secrets():
    """
    Carrega as credenciais do arquivo secrets.json de forma multiplataforma.
    
    Procura em:
    1. Diretório do arquivo atual (./config/secrets.json)
    2. Diretório de trabalho atual
    3. Diretório de configuração do usuário (~/.config/secrets.json)
    4. Variável de ambiente SECRETS_PATH (opcional)
    
    Returns:
        dict: Dicionário com as credenciais carregadas
        
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado em nenhum local
        json.JSONDecodeError: Se o arquivo estiver mal formatado
    """
    # Lista de locais possíveis para procurar o arquivo
    possible_locations = [
        Path(__file__).parent / "secrets.json",
        Path(__file__).parent / "config" / "secrets.json",
        Path.cwd() / "secrets.json",
        Path.home() / ".config" / "secrets.json",
        Path(os.getenv('APPDATA', '')) / "secrets.json",
    ]
    
    if env_path := os.getenv('SECRETS_PATH'):
        possible_locations.insert(0, Path(env_path))

    for location in possible_locations:
        try:
            if location.exists() and location.is_file():
                with open(location, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise json.JSONDecodeError(
                f"Erro ao decodificar JSON em {location}: {str(e)}",
                doc=str(location),
                pos=0
            ) from e
        except OSError:
            continue

    searched_paths = "\n".join(f"- {str(path)}" for path in possible_locations)
    raise FileNotFoundError(
        "Arquivo secrets.json não encontrado em nenhum dos locais:\n"
        f"{searched_paths}\n\n"
        "Por favor, crie o arquivo em um desses locais ou defina a variável "
        "de ambiente SECRETS_PATH com o caminho completo."
    )