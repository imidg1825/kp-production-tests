#!/bin/bash

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Installing Playwright browsers..."
playwright install

echo "==> Cleaning previous Allure data..."
rm -rf allure-results allure-report || true

echo "==> Running tests..."
pytest --alluredir=allure-results

echo "==> Generating Allure report..."
allure generate allure-results -o allure-report --clean

echo "==> Starting Allure server on port 4040..."
# стартуем сервер (WSL), слушаем на всех интерфейсах, чтобы VS Code мог пробросить порт
allure open allure-report --host 0.0.0.0 --port 4040 >/dev/null 2>&1 &

sleep 1

echo "==> Opening report in Windows browser..."
# пробуем открыть браузер на Windows (из WSL)
cmd.exe /c start http://localhost:4040 >/dev/null 2>&1 || true

echo "==> Done. If it didn't open, check VS Code -> PORTS -> 4040 and open via globe icon."
