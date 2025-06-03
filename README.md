# API Electrolux

## 📦 Instalação e Configuração

1. **Clone o repositório:**

```bash
git clone git@github.com:Novalar-Moveis-e-Eletrodomesticos/api_electrolux.git
```

2. **Acesse o diretório do projeto:**

```bash
cd api_electrolux
```

3. **Instale as dependências com o Poetry:**

```bash
poetry install
```

4. **Ative o ambiente virtual:**

```bash
eval "$(poetry env activate)"
```

## 🚀 Executando o Projeto

### 🔹 Ambiente de Produção

* Usando o Taskfile:

```bash
task run
```

* Diretamente com FastAPI:

```bash
fastapi run api_electrolux/main.py
```

### 🔹 Ambiente de Desenvolvimento

* Usando o Taskfile:

```bash
task dev
```

* Diretamente com FastAPI:

```bash
fastapi dev api_electrolux/main.py
```

## ✅ Observações

* Certifique-se de que o `Poetry`, `Task` e o `FastAPI` CLI estão instalados na sua máquina.
* Para variáveis de ambiente e configurações adicionais, consulte a documentação interna ou o arquivo `.env.example` (se houver).