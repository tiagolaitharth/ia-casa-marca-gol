@echo off

echo =========================
echo ATUALIZANDO MODELO...
echo =========================

python modelo.py

echo =========================
echo ENVIANDO PARA GITHUB...
echo =========================

git add .
git commit -m "update geral"
git push

echo =========================
echo FINALIZADO!
echo =========================

pause