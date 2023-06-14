#!/bin/bash

echo "=== Iniciando o Ritual de Banimento (VOID | QRcode) ==="
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
APP_NAME="qrcode-void-generator"
ICON_NAME="${APP_NAME}"

DESKTOP_ENTRY_DIR_USER="${HOME}/.local/share/applications"
ICON_INSTALL_SIZE_DIR_USER="${HOME}/.local/share/icons/hicolor/64x64/apps"
DESKTOP_ENTRY_DIR_SYSTEM="/usr/local/share/applications"
ICON_INSTALL_SIZE_DIR_SYSTEM="/usr/local/share/icons/hicolor/64x64/apps"

DESKTOP_FILE_PATH_USER="${DESKTOP_ENTRY_DIR_USER}/${APP_NAME}.desktop"
ICON_INSTALL_PATH_USER="${ICON_INSTALL_SIZE_DIR_USER}/${ICON_NAME}.png"
DESKTOP_FILE_PATH_SYSTEM="${DESKTOP_ENTRY_DIR_SYSTEM}/${APP_NAME}.desktop"
ICON_INSTALL_PATH_SYSTEM="${ICON_INSTALL_SIZE_DIR_SYSTEM}/${ICON_NAME}.png"

SUDO_CMD=""
if [[ -f "${DESKTOP_FILE_PATH_SYSTEM}" || -f "${ICON_INSTALL_PATH_SYSTEM}" ]]; then
    if [[ $(id -u) -ne 0 ]]; then
        SUDO_CMD="sudo"
        echo "Permissões elevadas (sudo) podem ser necessárias."
    fi
fi

echo "[1/3] Quebrando o círculo de proteção (venv)..."
rm -rf "${SCRIPT_DIR}/venv"

echo "[2/3] Apagando o sigilo de invocação (.desktop)..."
if [[ -f "${DESKTOP_FILE_PATH_USER}" ]]; then rm -f "${DESKTOP_FILE_PATH_USER}"; fi
if [[ -f "${DESKTOP_FILE_PATH_SYSTEM}" ]]; then $SUDO_CMD rm -f "${DESKTOP_FILE_PATH_SYSTEM}"; fi

echo "[3/3] Desconsagrando o ícone..."
if [[ -f "${ICON_INSTALL_PATH_USER}" ]]; then rm -f "${ICON_INSTALL_PATH_USER}"; fi
if [[ -f "${ICON_INSTALL_PATH_SYSTEM}" ]]; then $SUDO_CMD rm -f "${ICON_INSTALL_PATH_SYSTEM}"; fi

if command -v update-desktop-database &> /dev/null; then
    if [[ -d "${DESKTOP_ENTRY_DIR_USER}" ]]; then update-desktop-database "${DESKTOP_ENTRY_DIR_USER}" >/dev/null 2>&1; fi
    if [[ -d "${DESKTOP_ENTRY_DIR_SYSTEM}" ]]; then $SUDO_CMD update-desktop-database "${DESKTOP_ENTRY_DIR_SYSTEM}" >/dev/null 2>&1; fi
fi
if command -v gtk-update-icon-cache &> /dev/null; then
     ICON_BASE_USER="$HOME/.local/share/icons/hicolor/"
     ICON_BASE_SYSTEM="/usr/local/share/icons/hicolor/"
     if [[ -d "$ICON_BASE_USER" ]]; then gtk-update-icon-cache "$ICON_BASE_USER" -f -t >/dev/null 2>&1; fi
     if [[ -d "$ICON_BASE_SYSTEM" ]]; then $SUDO_CMD gtk-update-icon-cache "$ICON_BASE_SYSTEM" -f -t >/dev/null 2>&1; fi
fi

echo "=== Banimento Concluído ==="
