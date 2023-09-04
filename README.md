<div align="center">



<div align="center">
<div style="text-align: center;">
  <h1 style="font-size: 2.2em;">VOID | <span style="color:#bd93f9;">QRcode</span></h1>

[![opensource](https://badges.frapsoft.com/os/v1/open-source.png?v=103)](#)
[![Licença](https://img.shields.io/badge/licença-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![Estrelas](https://img.shields.io/github/stars/AndreBFarias/QR-Code-Void-Generator.svg?style=social)](https://github.com/AndreBFarias/QR-Code-Void-Generator/stargazers) [![Contribuições](https://img.shields.io/badge/contribuições-bem--vindas-brightgreen.svg)](https://github.com/AndreBFarias/QR-Code-Void-Generator/issues) 
  
  
  <img src="assets/icon.png" width="200" alt="Logo VOID | QRcode">
</div>
</div></div>

**VOID | QRcode** é uma ferramenta moderna e elegante para gerar QR Codes personalizados, com suporte para logos, cores, e diversos formatos de payload (Wi-Fi, Pix, Redes Sociais, etc.).


![Interface Principal](assets/interface.png)

## Funcionalidades

*   **Gerador de QR Code**: Criação rápida de QR Codes.
*   **Personalização**:
    *   Cores personalizadas (Fundo e Preenchimento).
    *   Logos centralizados (Upload ou presets).
    *   Estilos de pontos (Quadrado, Arredondado, etc.).
    *   Controle de opacidade e tamanho do logo.
*   **Payloads Suportados**:
    *   Texto Livre / URL.
    *   Wi-Fi (Detecção automática no Linux).
    *   Pix (Pagamentos instantâneos).
    *   Redes Sociais (Instagram, WhatsApp, etc.).
    *   Email, SMS, Telefone.
*   **Interface Moderna**: Tema escuro (Dracula), design responsivo e intuitivo.
*   **Exportação**: Salvar em PNG, JPG, PDF, SVG.

## Instalação

### Pré-requisitos

*   Python 3.10+
*   Linux (Testado no Ubuntu/Debian)

### Instalação Automática

Execute o script de instalação:

```bash
chmod +x install.sh
./install.sh
```

Isso criará um ambiente virtual, instalará as dependências e criará um atalho no menu de aplicativos.

### Instalação Manual

1.  Clone o repositório:
    ```bash
    git clone https://github.com/AndreBFarias/QR-Code-Void-Generator.git
    cd QR-Code-Void-Generator
    ```

2.  Crie e ative o ambiente virtual:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## Como Usar

Execute o aplicativo:

```bash
python3 main.py
```

Ou use o atalho "VOID | QRcode" no seu menu de aplicativos.

## Estrutura do Projeto

*   `main.py`: Ponto de entrada da aplicação.
*   `core/`: Lógica de negócio (geração, payloads, utils).
*   `ui/`: Interface gráfica (PyQt6).
*   `assets/`: Recursos estáticos (ícones, logos).

## Licença

Este projeto está licenciado sob a licença MIT.
