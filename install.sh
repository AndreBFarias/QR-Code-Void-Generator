#!/bin/bash
#
# RITUAL DE CONSAGRAÇÃO: VOID | QRcode
#

echo "=== Iniciando o Ritual de Instalação (VOID | QRcode) ==="
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_NAME="qrcode-void-generator"
APP_DISPLAY_NAME="VOID | QRcode"
ICON_NAME="${APP_NAME}"
ICON_SOURCE_PATH="${SCRIPT_DIR}/assets/icon.png"

# Destinos
DESKTOP_ENTRY_DIR_USER="${HOME}/.local/share/applications"
ICON_INSTALL_SIZE_DIR_USER="${HOME}/.local/share/icons/hicolor/64x64/apps"
DESKTOP_ENTRY_DIR_SYSTEM="/usr/local/share/applications"
ICON_INSTALL_SIZE_DIR_SYSTEM="/usr/local/share/icons/hicolor/64x64/apps"

# Escolhe diretório (prioriza usuário)
INSTALL_DIR=""
ICON_INSTALL_DIR=""
SUDO_CMD=""
mkdir -p "${DESKTOP_ENTRY_DIR_USER}"
mkdir -p "${ICON_INSTALL_SIZE_DIR_USER}"

if [[ -w "${DESKTOP_ENTRY_DIR_USER}" && -w "${ICON_INSTALL_SIZE_DIR_USER}" ]]; then
    INSTALL_DIR="${DESKTOP_ENTRY_DIR_USER}"
    ICON_INSTALL_DIR="${ICON_INSTALL_SIZE_DIR_USER}"
    echo "Instalando para o usuário atual (${USER})."
else
    echo "Diretório do usuário não gravável ou inexistente. Tentando instalação no sistema (requer sudo)."
    INSTALL_DIR="${DESKTOP_ENTRY_DIR_SYSTEM}"
    ICON_INSTALL_DIR="${ICON_INSTALL_SIZE_DIR_SYSTEM}"
    SUDO_CMD="sudo"
fi
DESKTOP_FILE_PATH="${INSTALL_DIR}/${APP_NAME}.desktop"
ICON_INSTALL_PATH="${ICON_INSTALL_DIR}/${ICON_NAME}.png"

# 1. Atualizar repositórios
echo "[1/5] Atualizando selos arcanos (apt update)..."
sudo apt update || { echo "ERRO: Falha ao atualizar repositórios apt."; exit 1; }

# 2. Instalar dependências do sistema
echo "[2/5] Invocando dependências (Python3, PIP, VENV)..."
sudo apt install -y python3-pip python3-venv desktop-file-utils imagemagick || { echo "ERRO: Falha ao instalar dependências do sistema."; exit 1; }

# 3. Criar ambiente virtual
echo "[3/5] Desenhando círculo de proteção (venv)..."
if [ -d "${SCRIPT_DIR}/venv" ]; then
    echo "Removendo venv antigo..."
    rm -rf "${SCRIPT_DIR}/venv"
fi
python3 -m venv "${SCRIPT_DIR}/venv" || { echo "ERRO: Falha ao criar ambiente virtual."; exit 1; }

# 4. Instalar dependências Python no venv
echo "[4/5] Instalando pacotes Python no venv..."
if [ ! -f "${SCRIPT_DIR}/requirements.txt" ]; then
    echo "ERRO: requirements.txt não encontrado em ${SCRIPT_DIR}!"
    exit 1
fi
"${SCRIPT_DIR}/venv/bin/pip" install --upgrade pip || echo "Aviso: Falha ao atualizar pip."
"${SCRIPT_DIR}/venv/bin/pip" install -r "${SCRIPT_DIR}/requirements.txt" || { echo "ERRO: Falha ao instalar pacotes Python."; exit 1; }

# 5. Instalar o Ícone e Criar Lançador
echo "[5/5] Consagrando o ícone e forjando o sigilo..."
if [ ! -f "${ICON_SOURCE_PATH}" ]; then
    echo "ERRO: Ícone '${ICON_SOURCE_PATH}' não encontrado!"
    exit 1
fi
$SUDO_CMD mkdir -p "${ICON_INSTALL_DIR}"
if command -v convert &> /dev/null; then
     $SUDO_CMD convert "${ICON_SOURCE_PATH}" -resize 64x64 "${ICON_INSTALL_PATH}" || { echo "ERRO: Falha ao redimensionar ícone."; exit 1; }
else
     echo "ERRO: 'convert' não encontrado."
     exit 1
fi

# Atualiza cache de ícones
if command -v gtk-update-icon-cache &> /dev/null; then
    CACHE_DIR=""
    if [[ -n "$SUDO_CMD" ]]; then CACHE_DIR="/usr/local/share/icons/hicolor/"; else CACHE_DIR="$HOME/.local/share/icons/hicolor/"; fi
    if [[ -d "$CACHE_DIR" ]]; then $SUDO_CMD gtk-update-icon-cache "$CACHE_DIR" -f -t; fi
fi

# Criar .desktop
$SUDO_CMD mkdir -p "${INSTALL_DIR}"
PYTHON_VENV_PATH="${SCRIPT_DIR}/venv/bin/python3"
MAIN_SCRIPT_PATH="${SCRIPT_DIR}/main.py"
EXEC_COMMAND="\"${PYTHON_VENV_PATH}\" \"${MAIN_SCRIPT_PATH}\""
CATEGORIES="Utility;Graphics;"

$SUDO_CMD printf "[Desktop Entry]\nVersion=1.0\nName=%s\nComment=Gerador de QR Code com Estilo\nExec=%s\nIcon=%s\nTerminal=false\nType=Application\nCategories=%s\nStartupNotify=true\nStartupWMClass=%s\nPath=%s\n" \
    "${APP_DISPLAY_NAME}" \
    "${EXEC_COMMAND}" \
    "${ICON_NAME}" \
    "${CATEGORIES}" \
    "${APP_NAME}" \
    "${SCRIPT_DIR}" \
    > "${DESKTOP_FILE_PATH}" || { echo "ERRO: Falha ao criar arquivo .desktop."; exit 1; }

# Atualiza database
if command -v update-desktop-database &> /dev/null; then
    DB_DIR=""
    if [[ -n "$SUDO_CMD" ]]; then DB_DIR="${DESKTOP_ENTRY_DIR_SYSTEM}"; else DB_DIR="${DESKTOP_ENTRY_DIR_USER}"; fi
    if [[ -d "$DB_DIR" ]]; then $SUDO_CMD update-desktop-database "${DB_DIR}"; fi
fi

echo "=== Ritual Concluído ==="
echo "Você agora pode encontrar '${APP_DISPLAY_NAME}' no seu menu de aplicativos."
