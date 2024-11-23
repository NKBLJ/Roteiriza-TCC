# **Sistema de Roteirização - Roteiriza**

Este repositório contém um sistema de roteirização que utiliza APIs externas para otimização de rotas e cálculos geográficos. O projeto foi desenvolvido para integrar bases de dados e serviços de mapas, garantindo flexibilidade e precisão na construção de itinerários.

## **Pré-requisitos**

Antes de começar, certifique-se de ter as seguintes ferramentas instaladas:
- **Python 3.8+**
- **Git**
- Gerenciador de pacotes **pip**

Certifique-se também de ter acesso às chaves das APIs e ao banco de dados configurado.

---

## **Instalação**

1. Clone este repositório:
   ```bash
   git clone [https://github.com/NKBLJ/Roteiriza-TCC.git]
   cd Roteiriza-TCC
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente em um arquivo `.env` na raiz do projeto.

---

## **Configuração**

Crie um arquivo `.env` e adicione as seguintes variáveis:

```env
DATABASE_URL=postgresql://usuario:senha@host:porta/nome_banco
GOOGLE_MAPS_API_KEY=sua_chave_google_maps
OPENROUTE_API_KEY=sua_chave_openroute
SECRET_KEY=sua_chave_secreta
TOKEN_CRIAR_ACESSO=token_para_criar_acesso
```

### **Descrição das Variáveis**

- `DATABASE_URL`: String de conexão com o banco de dados.
- `GOOGLE_MAPS_API_KEY`: Chave de acesso à API do Google Maps.
- `OPENROUTE_API_KEY`: Chave de acesso à API OpenRoute.
- `SECRET_KEY`: Chave secreta usada no sistema (ex: para criptografia ou autenticação).
- `TOKEN_CRIAR_ACESSO`: Token necessário para realizar requisições seguras no sistema.

---

## **Como Usar**

1. Execute o sistema:
   ```bash
   python app.py
   ```

2. Acesse o sistema no navegador:
   ```
   http://127.0.0.1:5000
   ```

3. Use as funcionalidades de roteirização.

---

## **Contribuições**

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork deste repositório.
2. Crie uma branch com sua feature ou correção:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça commit das alterações:
   ```bash
   git commit -m "Adiciona minha nova feature"
   ```
4. Envie para o repositório remoto:
   ```bash
   git push origin minha-feature
   ```
5. Abra um Pull Request.

---

Se precisar de ajuda, abra uma **issue** no repositório! 😊
