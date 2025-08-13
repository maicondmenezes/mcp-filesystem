import inspect
import json
from typing import Any, Callable, Dict, List, Mapping, Type, Union

from pydantic import BaseModel, ValidationError

from mcp_filesystem.services.filesystem_service import FilesystemService
from mcp_filesystem.storage.filesystem_storage import FilesystemStorage


class McpFilesystemController:
    """
    Controlador para o MCP Filesystem, responsável por gerenciar e executar
    ferramentas do serviço de sistema de arquivos.
    """

    def __init__(self, allowed_directories: List[str]):
        """
        Inicializa o controlador, o storage e o serviço.

        Args:
            allowed_directories: Lista de diretórios onde operações são permitidas.
        """
        storage = FilesystemStorage(allowed_directories=allowed_directories)
        self.filesystem_service = FilesystemService(storage=storage)
        self.tools = self._discover_tools()

    def _discover_tools(self) -> Mapping[str, Callable[..., Any]]:
        """
        Descobre as ferramentas disponíveis no FilesystemService.

        Returns:
            Um dicionário mapeando nomes de ferramentas para seus métodos.
        """
        tools: Dict[str, Callable[..., Any]] = {}
        for name, method in inspect.getmembers(
            self.filesystem_service, predicate=inspect.ismethod
        ):
            if not name.startswith("_"):
                tools[name] = method
        return tools

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Obtém a lista de ferramentas disponíveis com seus esquemas de entrada.

        Returns:
            Uma lista de dicionários, cada um representando uma ferramenta.
        """
        tool_list = []
        for name, method in self.tools.items():
            input_schema = self._get_input_schema(method)
            tool_info = {
                "name": name,
                "description": inspect.getdoc(method) or "Sem descrição.",
                "input_schema": input_schema,
            }
            tool_list.append(tool_info)
        return tool_list

    def _get_input_schema(
        self, method: Callable[..., Any]
    ) -> Union[Dict[str, Any], None]:
        """
        Obtém o esquema de entrada para um método de ferramenta.

        Args:
            method: O método da ferramenta.

        Returns:
            O esquema de entrada Pydantic como um dicionário, ou None se não houver.
        """
        sig = inspect.signature(method)
        if not sig.parameters:
            return None

        param = next(iter(sig.parameters.values()))
        model: Type[BaseModel] = param.annotation

        if not inspect.isclass(model) or not issubclass(model, BaseModel):
            return None

        return model.model_json_schema()

    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma ferramenta com os argumentos fornecidos.

        Args:
            tool_name: O nome da ferramenta a ser executada.
            args: Os argumentos para a ferramenta.

        Returns:
            Um dicionário contendo o resultado da execução ou um erro.
        """
        if tool_name not in self.tools:
            return {"error": f"Ferramenta '{tool_name}' não encontrada."}

        method = self.tools[tool_name]
        sig = inspect.signature(method)

        try:
            if not sig.parameters:
                result = method()
            else:
                param = next(iter(sig.parameters.values()))
                model: Type[BaseModel] = param.annotation

                if not inspect.isclass(model) or not issubclass(model, BaseModel):
                    result = method(**args)
                else:
                    validated_args = model(**args)
                    result = method(validated_args)

            if isinstance(result, str):
                return {"content": result}
            return {"result": self._serialize_result(result)}

        except ValidationError as e:
            return {"error": f"Erro de validação: {e}", "tool": tool_name}
        except Exception as e:
            return {"error": str(e), "tool": tool_name}

    def _serialize_result(self, result: Any) -> Any:
        """
        Serializa o resultado da execução de uma ferramenta para um formato
        compatível com JSON.

        Args:
            result: O resultado da execução da ferramenta.

        Returns:
            O resultado serializado.
        """
        if isinstance(result, (str, int, float, bool, type(None))):
            return result
        if isinstance(result, (list, tuple)):
            return [self._serialize_result(item) for item in result]
        if isinstance(result, dict):
            return {key: self._serialize_result(value) for key, value in result.items()}
        if isinstance(result, BaseModel):
            return result.dict()

        try:
            return json.dumps(result)
        except TypeError:
            return str(result)
