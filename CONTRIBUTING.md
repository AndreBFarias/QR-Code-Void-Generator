# Guia de Contribuição -- QR-Code-Void-Generator

## Como Contribuir

1. Fork → branch feature → PR contra `main`
2. Commits em PT-BR (Conventional Commits)

## Padrão

- PT-BR com acentuação correta
- Zero emojis, zero menção IA
- Type hints sempre
- `logging` (nunca print em produção)

## Configuração

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Testes

```bash
pytest tests/ -v
```
