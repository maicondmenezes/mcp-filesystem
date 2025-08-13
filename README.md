# MCP Filesystem

🚀 **Servidor MCP (Model Context Protocol) seguro para operações de sistema de arquivos**

Este projeto fornece um servidor MCP que permite acesso controlado ao sistema de arquivos através de uma interface padronizada, compatível com Claude Desktop e outros clientes MCP.

## ✨ Funcionalidades

### 🔧 Ferramentas Disponíveis (11 total)

| Ferramenta | Descrição |
|------------|-----------|
| `read_text_file` | Lê arquivos de texto com opções head/tail |
| `read_multiple_files` | Lê múltiplos arquivos simultaneamente |
| `write_file` | Escreve conteúdo em arquivos |
| `edit_file` | Edita arquivos com operações find/replace + dry-run |
| `create_directory` | Cria diretórios |
| `list_directory` | Lista conteúdo de diretórios (simples) |
| `list_directory_with_sizes` | Lista diretórios com informações detalhadas |
| `get_file_info` | Obtém metadados de arquivos/diretórios |
| `search_files` | Busca arquivos por padrões (glob/regex) |
| `move_file` | Move/renomeia arquivos |
| `delete_file` | Remove arquivos/diretórios (com suporte recursivo) |

### 🔒 Recursos de Segurança

- **Controle de diretórios permitidos** configurável via `--allowed-dirs`
- **Validação rigorosa de caminhos** para prevenir acessos não autorizados
- **Comunicação via stdio** (sem exposição de rede)
- **Validação de entrada** com Pydantic para todos os parâmetros

## 📦 Instalação e Configuração

### Quick Start

```bash
# 1. Configurar ambiente de desenvolvimento
make setup-dev

# 2. Executar testes
make test

# 3. Iniciar servidor em modo desenvolvimento
make start-dev-env
```

### Pré-requisitos

- Python 3.12+
- Poetry
- pyenv (recomendado)

### Comandos Make Disponíveis

#### Setup e Dependências
- `make setup-dev` - Configura ambiente completo (Python, dependências, hooks)
- `make install` - Instala dependências usando Poetry
- `make check-deps` - Verifica se pyenv e poetry estão instalados
- `make install-deps` - Mostra instruções de instalação das ferramentas
- `make set-pre-commit` - Instala hooks do pre-commit

#### Desenvolvimento
- `make start-dev-env` - Inicia servidor MCP em modo desenvolvimento
- `make run` - Executa o CLI da aplicação

#### Qualidade de Código e Testes
- `make format` - Formata código (black + isort)
- `make lint` - Executa linters (flake8 + mypy)
- `make test` - Executa testes com coverage
- `make test-verbose` - Executa testes em modo verboso

#### Docker
- `make build-docker` - Constrói imagem Docker

#### Limpeza
- `make clean` - Remove arquivos temporários
- `make clean-all` - Limpeza completa (incluindo .venv)

## 🚀 Uso

### Linha de Comando

```bash
# Iniciar com diretório atual
mcp-filesystem start

# Especificar diretórios permitidos
mcp-filesystem start --allowed-dirs /home/user/projects --allowed-dirs /tmp

# Validar diretórios
mcp-filesystem validate-dirs /path/to/dir1 /path/to/dir2

# Verificar versão
mcp-filesystem version
```

### Integração com Claude Desktop

```json
{
  "servers": {
    "filesystem": {
      "command": "poetry",
      "args": ["run", "mcp-filesystem", "start", "--allowed-dirs", "/home/user/projects"],
      "cwd": "/path/to/mcp-filesystem"
    }
  }
}
```

## 🧪 Testes

```bash
# Testes completos com coverage
make test

# Testes verbosos
make test-verbose

# Linting
make lint
```

## 🏗️ Arquitetura

```
CLI (main.py) → MCP Server → Controller → Service → Storage
```

- **CLI**: Interface de linha de comando (Typer)
- **MCP Server**: Implementação do protocolo MCP via stdio
- **Controller**: Descoberta automática de ferramentas e coordenação
- **Service**: Lógica de negócios com validação Pydantic
- **Storage**: Operações seguras no sistema de arquivos

## 🛠️ Desenvolvimento

### Configuração Inicial

```bash
# Setup completo
make setup-dev

# Apenas dependências
make install

# Hooks pre-commit
make set-pre-commit
```

### Formatação e Qualidade

```bash
# Formatar código
make format

# Verificar qualidade
make lint
```

## 📝 Exemplos de Uso

### Lendo Arquivos

```json
{
  "name": "read_text_file",
  "arguments": {
    "path": "/tmp/example.txt",
    "head": 10
  }
}
```

### Escrevendo Arquivos

```json
{
  "name": "write_file",
  "arguments": {
    "path": "/tmp/new_file.txt",
    "content": "Hello, MCP Filesystem!"
  }
}
```

### Listando Diretórios

```json
{
  "name": "list_directory_with_sizes",
  "arguments": {
    "path": "/tmp"
  }
}
```

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch: `git checkout -b feat/nova-feature`
3. Faça suas alterações e teste: `make test`
4. Execute a formatação: `make format`
5. Verifique a qualidade: `make lint`
6. Commit: `git commit -m 'feat: adiciona nova feature'`
7. Push: `git push origin feat/nova-feature`
8. Abra um Pull Request

---

**✅ Pronto para usar com Claude Desktop! 🎉**
