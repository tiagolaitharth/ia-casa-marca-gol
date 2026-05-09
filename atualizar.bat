@echo off

cd /d "C:\Users\Pichau\OneDrive\testebanco"

echo =========================
echo TREINANDO IA
echo =========================

python modelo.py

echo =========================
echo ENVIANDO PARA GITHUB
echo =========================

git add .

git commit -m "Atualizacao automatica"

git push

echo =========================
echo FINALIZADO
echo =========================

pause