# Política de Segurança -- QR-Code-Void-Generator

## Versões Suportadas

| Versão | Suportada |
| ------ | --------- |
| 2.0.x  | sim       |

## Dados Sensíveis

QR Codes gerados podem conter:

- Chaves PIX (email, CPF, telefone) -- informação potencialmente sensível
- URLs privadas
- Dados de contato

**Não commite** QR codes gerados com dados reais no repositório. O `.gitignore` deve excluir `*.png` e `*.jpg` de teste.

## Reportando

1. **Não** abra issue pública
2. Email ao mantenedor
3. Tempo: 48h recepção / 7d avaliação / 30d correção

## Escopo

- `core/`, `ui/`
- Scripts de instalação
- CI

## Fora do Escopo

- `qrcode`, `Pillow`, `PyQt6` (upstream)
