#!/bin/bash

# Script para iniciar o servidor local do Gerenciador de Investimentos

echo "🚀 Iniciando Gerenciador de Investimentos..."
echo ""
echo "📊 Acesse o aplicativo em: http://localhost:8000"
echo "📚 Guia rápido: http://localhost:8000/guia.html"
echo ""
echo "💡 Pressione Ctrl+C para parar o servidor"
echo ""

# Verifica se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3 para continuar."
    exit 1
fi

# Inicia o servidor
python3 -m http.server 8000
