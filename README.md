> [!WARNING]  
> A ferramenta é básica e ainda está em fase de desenvolvimento. Novas melhorias e recursos serão adicionados em breve...

---

# XRAV JUSBR

Esta ferramenta foi desenvolvida exclusivamente para fins educacionais, de pesquisa, investigação, produção de inteligência e suporte técnico. Seu objetivo é automatizar a extração de informações públicas disponíveis no site Jusbrasil, utilizando um mecanismo de **triangulação de dados** entre nome e CPF do alvo.

Após localizar o alvo, a ferramenta consolida automaticamente os dados coletados em relatórios estruturados, facilitando a análise e a utilização das informações.

[![Licença: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)

### 🎯 Funcionalidades

- **Detecção Automática de Nome**: Identifica automaticamente o nome da pessoa pesquisada na página de resultados do Jusbrasil.
- **Busca Inteligente por CPF**: Utiliza máscaras personalizadas para localizar CPFs específicos, retornando a URL quando encontrado.
- **Triangulação de Informações**: Cruza dados de nome e CPF para validar e consolidar informações do alvo.
- **Extração de Dados**: Coleta informações como idade, estado (UF) e empresas vinculadas.
- **Relatórios Detalhados**: Gera arquivo `.txt` com todas as informações relevantes extraídas.
- **Interface Amigável**: UI moderna e interativa diretamente no console do navegador.

## 🛠️ Setup e Geração do Script

Para gerar o arquivo `devtools-xrav-jusbr-YYYYMMDD_HHMMSS.txt` que contém o script a ser executado no navegador, siga os procedimentos abaixo.

### 📥 Instalação

1. Baixe o projeto/script diretamente do repositório.
2. Extraia os arquivos em uma pasta de sua preferência.
3. Navegue até a pasta onde o script foi extraído.
4. Abra o **PowerShell** ou **Prompt de Comando**.
5. Execute o gerador:
```powershell
python xrav-jusbr.py
```

### 📄 Resultado

Após a execução, o arquivo será gerado automaticamente no diretório atual com a seguinte nomenclatura:
```
devtools-xrav-jusbr-YYYYMMDD_HHMMSS.txt
```

**Exemplo:** `devtools-xrav-jusbr-20260717_051837.txt`

> ⚠️ **Nota:** Certifique-se de ter o Python 3.6+ instalado em seu sistema. Para verificar, execute `python --version` no terminal.

## 🚀 Como Usar

1. **Acesse o [Jusbrasil](https://www.jusbrasil.com.br)** e realize a busca pela pessoa desejada.
2. **Abra o Console do Navegador**:
   - Pressione `F12` (ou `Ctrl+Shift+I`).
   - Vá para a aba `Console`.
3. **Cole o Script**: Copie o conteúdo do arquivo gerado e cole no console.
4. **Pressione `ENTER`**: A interface de XRAV JUSBR aparecerá.
5. **Preencha os Dados**:
   - O nome será detectado automaticamente pela ferramenta.
   - Insira a máscara do CPF desejada (ex: `***.123.123-**`).
   - Ajuste o delay entre requisições, se necessário.
6. **Clique em `INICIAR`** e aguarde os resultados.
   - O sistema realizará a busca parametrizada, cruzando as informações.
   - Ao encontrar o alvo, retornará a URL correspondente.
   - Todos os dados serão consolidados em um relatório detalhado.

### Exemplo de Máscara CPF

| Máscara | Descrição |
|---------|-----------|
| `***.123.123-**` | Busca CPFs com os dígitos centrais |
| `123.123.123-**` | Busca CPFs com os primeiros 9 dígitos fixos |

> Use `*` (asterisco) para representar dígitos desconhecidos. A ferramenta utiliza esta máscara para realizar a busca e, quando o CPF é localizado, retorna a URL exata do resultado encontrado.

## ⚖️ Base Legal e Normas Técnicas

O uso desta ferramenta deve estar em conformidade com as seguintes normas e legislações:

### Normas ISO
- **ISO/IEC 27001** – Gestão da Segurança da Informação.
- **ISO/IEC 27042** – Diretrizes para análise e interpretação de evidências digitais.
- **ISO/IEC 27037** – Diretrizes para identificação, coleta e preservação de evidências digitais.

### Referências Técnicas
- **NIST IR 8387** – Investigação digital e preservação de evidências.

### Legislação Brasileira
- **Cadeia de custódia** – CPP, Arts. 158-A a 158-F.
- **Art. 159 §4º CPP** – Assistência Técnica em Perícias Digitais.
- **Lei nº 13.432/2017** – Produção de inteligência e suporte técnico.

## 💡 Recomendação Complementar

Recomendamos utilizar a ferramenta complementar [`zcpf-finder`](https://github.com/zr0n/zcpf-finder) para busca em massa de CPFs no Portal da Transparência, permitindo validar e cruzar informações com bases governamentais.

## ⚠️ Aviso Legal

Esta ferramenta foi desenvolvida **exclusivamente para fins educacionais, de pesquisa, investigação, produção de inteligência e suporte técnico**. O usuário declara estar plenamente ciente e responsável pelo uso que fizer dela, comprometendo-se a:

- **Cumprir integralmente** todas as legislações de privacidade e proteção de dados aplicáveis (como LGPD, GDPR e demais normas pertinentes).  
- **Utilizar a ferramenta apenas** para finalidades legítimas, lícitas e sempre com o devido consentimento.  
- **Abster-se de empregar os dados extraídos** para práticas discriminatórias, ilícitas ou que atentem contra direitos fundamentais.  
- **Reconhecer que esta ferramenta não substitui** perícias oficiais, investigações formais ou funções públicas legalmente constituídas.  
