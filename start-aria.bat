@echo off
echo ========================================
echo   ARIA - AI Model Lab
echo   Starting Docker services...
echo ========================================
echo.

REM Stop any existing containers
docker-compose down 2>nul

REM Pull latest images
echo Pulling latest images...
docker-compose pull

REM Start services
echo Starting Ollama and Web UI...
docker-compose up -d

echo.
echo Waiting for Ollama to initialize...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   ARIA is running!
echo   Web UI: http://localhost:8080
echo   Ollama: http://localhost:11434
echo ========================================
echo.
echo To stop: docker-compose down
echo To view logs: docker-compose logs -f
echo.
echo Pull a model first (if you haven't):
echo   docker exec -it ollama ollama pull smollm2
echo   docker exec -it ollama ollama pull mistral
echo ========================================

@echo off
set ANTHROPIC_BASE_URL=http://localhost:11434/v1
set ANTHROPIC_API_KEY=ollama
docker compose up -d
claude
