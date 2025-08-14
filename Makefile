SHELL := /bin/bash
.PHONY: help \
				check-deps \
				install-deps \
				setup-dev \
				set-pre-commit \
				lint \
				format \
				test \
				start-dev-env \
				clean \
				run \
				build-docker \
				config-copilot \
				config-gemini \
				config-cline \
				test-mcp \
				test-copilot \
				test-gemini \
				test-cline

PYTHON_VERSION := 3.12
PROJECT_NAME := mcp-filesystem
PROJECT_DIR := $(shell pwd)

default: help

# ====================================================================================
# HELP
# ====================================================================================

help: ## Show this help message
	@echo "🚀 MCP Filesystem - Development Environment"
	@echo "========================================================================"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "💡 Quick start:"
	@echo "   1. make setup-dev"
	@echo "   2. make test"
	@echo "   3. make start-dev-env"
	@echo ""
	@echo "🤖 AI Client Configuration:"
	@echo "   make config-copilot   - Configure for GitHub Copilot"
	@echo "   make config-gemini    - Configure for Gemini Code Assist"
	@echo "   make config-cline     - Configure for Cline"
	@echo ""
	@echo "🧪 MCP Testing:"
	@echo "   make test-mcp         - Test all AI clients connectivity"
	@echo "   make test-copilot     - Test GitHub Copilot configuration"
	@echo "   make test-gemini      - Test Gemini Code Assist configuration"
	@echo "   make test-cline       - Test Cline configuration"
	@echo ""

# ====================================================================================
# SETUP & DEPENDENCIES
# ====================================================================================

check-deps: ## Verifica se as dependências (pyenv, poetry) estão instaladas
	@echo "🔍 Verificando dependências..."
	@command -v pyenv >/dev/null 2>&1 || { echo "❌ pyenv não encontrado. Execute 'make install-deps'"; exit 1; }
	@command -v poetry >/dev/null 2>&1 || { echo "❌ poetry não encontrado. Execute 'make install-deps'"; exit 1; }
	@echo "✅ Todas as dependências foram encontradas!"

install-deps: ## Mostra instruções para instalar as ferramentas de desenvolvimento
	@echo "📦 Instruções de Instalação:"
	@echo "--------------------------------------------------"
	@echo "1. Instale o pyenv (gerenciador de versão do Python):"
	@echo "   curl https://pyenv.run | bash"
	@echo ""
	@echo "2. Instale o poetry (gerenciador de dependências):"
	@echo "   curl -sSL https://install.python-poetry.org | python3 -"
	@echo ""
	@echo "3. Após a instalação, configure seu shell (e.g., ~/.zshrc ou ~/.bashrc) e reinicie o terminal."

setup-dev: ## Configura o ambiente de desenvolvimento completo (Python, dependências, hooks)
	@if ! make check-deps >/dev/null 2>&1; then \
		echo "⚠️  Algumas dependências de desenvolvimento não foram encontradas."; \
		read -p "🤔 Deseja instalar as dependências agora? (S/n): " answer; \
		if [[ "$$answer" =~ ^[Ss]$$ || "$$answer" == "" ]]; then \
			make install-deps; \
			echo "➡️  Por favor, siga as instruções, reinicie seu terminal e execute 'make setup-dev' novamente."; \
			exit 1; \
		else \
			echo "❌ Configuração cancelada. Instale as dependências e tente novamente."; \
			exit 1; \
		fi \
	fi
	@echo "✅ Dependências verificadas."
	@echo "🐍 Configurando ambiente Python com pyenv..."
	@if ! pyenv versions --bare | grep -q "^$(PYTHON_VERSION)"; then \
		echo "   Python $(PYTHON_VERSION) não encontrado, instalando via pyenv (isso pode levar alguns minutos)..."; \
		pyenv install $(PYTHON_VERSION); \
	else \
		echo "   Python $(PYTHON_VERSION) já está disponível."; \
	fi
	@pyenv local $(PYTHON_VERSION)
	@poetry config virtualenvs.in-project true
	@echo "📦 Instalando dependências do projeto com Poetry..."
	@poetry install
	@echo "🪝 Configurando pre-commit hooks..."
	@make set-pre-commit
	@echo "🎉 Ambiente de desenvolvimento configurado com sucesso!"

install: ## Instala as dependências usando Poetry
	@echo "📦 Instalando dependências..."
	@poetry install

set-pre-commit: ## Instala os hooks de git do pre-commit
	@echo "🪝 Instalando pre-commit hooks..."
	@poetry run pre-commit install
	@echo "✅ Hooks instalados."

# ====================================================================================
# DEVELOPMENT
# ====================================================================================

start-dev-env: ## Inicia o servidor MCP em modo de desenvolvimento
	@echo "🚀 Iniciando servidor MCP Filesystem..."
	@echo "📁 Usando diretório atual como permitido: $(PWD)"
	@echo "⚡ Executando servidor em modo stdio..."
	@poetry run mcp-filesystem start --allowed-dirs $(PWD)

run: ## Executa o CLI da aplicação
	@poetry run mcp-filesystem

# ====================================================================================
# CODE QUALITY & TESTING
# ====================================================================================

format: ## Formata o código usando black e isort
	@echo "🎨 Formatando código..."
	@poetry run black mcp_filesystem tests
	@poetry run isort mcp_filesystem tests
	@echo "✅ Código formatado."

lint: ## Executa os linters para verificar a qualidade do código
	@echo "🔍 Executando linters..."
	@poetry run flake8 mcp_filesystem tests
	@poetry run mypy mcp_filesystem
	@echo "✅ Linting completo."

test: ## Executa os testes unitários com coverage
	@echo "🧪 Executando testes com coverage..."
	@poetry run pytest --cov=mcp_filesystem --cov-report=html --cov-report=term
	@echo "✅ Testes concluídos. Relatório HTML em htmlcov/"

test-verbose: ## Executa os testes em modo verboso
	@echo "🧪 Executando testes em modo verboso..."
	@poetry run pytest -v --cov=mcp_filesystem

# ====================================================================================
# DOCKER
# ====================================================================================

build-docker: ## Constrói a imagem Docker
	@echo "🐳 Construindo imagem Docker..."
	@docker build -t $(PROJECT_NAME):latest .
	@echo "✅ Imagem construída: $(PROJECT_NAME):latest"

# ====================================================================================
# AI CLIENT CONFIGURATION
# ====================================================================================

config-copilot: ## Configura MCP automaticamente para GitHub Copilot
	@echo "🤖 Configurador automático do GitHub Copilot..."
	@python3 scripts/setup-ai-clients.py copilot

config-gemini: ## Configura MCP automaticamente para Gemini Code Assist
	@echo "🤖 Configurador automático do Gemini Code Assist..."
	@python3 scripts/setup-ai-clients.py gemini

config-cline: ## Configura MCP automaticamente para Cline
	@echo "🤖 Configurador automático do Cline..."
	@python3 scripts/setup-ai-clients.py cline

test-mcp: ## Testa conectividade MCP com todos os clientes
	@echo "🧪 Testando conectividade MCP..."
	@python3 scripts/test-mcp.py all

test-copilot: ## Testa configuração do GitHub Copilot
	@python3 scripts/test-mcp.py copilot

test-gemini: ## Testa configuração do Gemini Code Assist
	@python3 scripts/test-mcp.py gemini

test-cline: ## Testa configuração do Cline
	@python3 scripts/test-mcp.py cline

# ====================================================================================
# CLEANING
# ====================================================================================

clean: ## Remove arquivos temporários e de build
	@echo "🧹 Limpando arquivos temporários..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -rf .pytest_cache .coverage htmlcov .mypy_cache
	@rm -rf build/ dist/ *.egg-info/
	@echo "✅ Limpeza concluída."

clean-all: ## Remove tudo incluindo venv
	@echo "🧹 Limpeza completa (incluindo .venv)..."
	@make clean
	@if [ -d .venv ]; then rm -rf .venv; fi
	@echo "✅ Limpeza completa concluída."
