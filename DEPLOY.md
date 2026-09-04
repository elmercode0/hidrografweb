# Deploy — Hidrograf no Streamlit Community Cloud

App web: [`streamlit_app.py`](streamlit_app.py) (UI fina sobre a biblioteca `hidrograf`).

## Rodar localmente

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
# abre em http://localhost:8501
```

## Publicar (Streamlit Community Cloud — grátis, aberto)

Pré-requisito: o código precisa estar num repositório **GitHub** (público ou privado).

1. **Versionar e enviar ao GitHub**

   ```bash
   git init
   git add .
   git commit -m "Hidrograf: biblioteca, CLI e app Streamlit"
   git branch -M main
   git remote add origin https://github.com/<voce>/hidrografweb.git
   git push -u origin main
   ```

2. **Conectar no Streamlit Cloud**
   - Acesse **https://share.streamlit.io** e entre com o GitHub.
   - **Create app → Deploy a public app from GitHub**.
   - Preencha:
     - **Repository:** `<voce>/hidrografweb`
     - **Branch:** `main`
     - **Main file path:** `streamlit_app.py`
   - **Deploy**. Em ~1–2 min o app fica no ar numa URL pública
     `https://<slug>.streamlit.app`.

3. **Atualizações:** cada `git push` na branch redeploya automaticamente.

## Como o deploy funciona aqui

- O Streamlit Cloud instala as dependências de [`requirements.txt`](requirements.txt).
- A biblioteca `hidrograf` é importada de `src/` (o `streamlit_app.py` adiciona `src` ao
  `sys.path`) — não precisa publicá-la em PyPI.
- `matplotlib` roda com backend `Agg` (headless), definido no app.
- Configuração de tema/servidor em [`.streamlit/config.toml`](.streamlit/config.toml).

## Notas / limites

- **Recursos:** o tier gratuito tem RAM limitada (~1 GB) — suficiente para este app.
- **Dados:** processados em memória a cada sessão; nada é persistido.
- **Privacidade:** um app público fica acessível por qualquer pessoa com a URL. Use um
  repositório privado + app privado (ou senha via `st.secrets`) se necessário.

## Alternativas abertas (mesmo código-base)

- **Hugging Face Spaces** (SDK Streamlit): suba os mesmos arquivos num Space.
- **Render / Railway / Fly.io:** rode `streamlit run` num container (precisa `Dockerfile`
  ou start command `streamlit run streamlit_app.py --server.port $PORT`).
