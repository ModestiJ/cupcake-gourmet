# Deploy – Render + Neon (gratuito)

Tempo estimado: 15 minutos.

## 1. Banco de dados (Neon)
1. Crie uma conta em https://neon.tech (dá para entrar com o GitHub).
2. **Create project** → nome `cupcake-gourmet`, Postgres 17, região **AWS São Paulo (sa-east-1)** ou US East.
3. Em **Connection details**, copie a *connection string* (formato `postgresql://usuario:senha@ep-...neon.tech/neondb?sslmode=require`).

## 2. Aplicação (Render)
1. Crie uma conta em https://render.com com o GitHub.
2. **New → Blueprint** → selecione o repositório. O Render lê o `render.yaml`.
3. Preencha as variáveis pedidas:
   - `DATABASE_URL`: a string do Neon
   - `ADMIN_EMAIL`: e-mail do administrador da loja
   - `ADMIN_PASSWORD`: senha forte (não use a mesma de outras contas)
4. **Apply.** O build (`build.sh`) instala as dependências, coleta os estáticos, roda as migrations e o `seed` (cupcakes, zonas, admin e cliente demo).
5. A URL fica no formato `https://cupcake-gourmet-xxxx.onrender.com`.

## 3. Atualizações
Todo `git push` na branch `main` dispara um novo deploy automático. O GitHub Actions roda os testes em Postgres a cada push.

## 4. Manutenção
- Repor o estoque de demonstração: no Render, **Shell** → `python manage.py seed --repor-estoque`.
- Criar outro admin: **Shell** → `python manage.py createsuperuser`.
