#!/usr/bin/env python3
"""Rebuild this specific translation from the user's original executable."""
from pathlib import Path
import hashlib,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent
EXPECTED='6c94702a7096dcc5e048e0eaeefd2d939ccfc6502d241458c805d4c97f67f7c8'
if len(sys.argv)!=3:
 raise SystemExit('Uso: python3 reconstruir.py /original/sm64corrigido.xex /ferramentas/XexTool')
source=Path(sys.argv[1]).resolve();tool=Path(sys.argv[2]).resolve()
if hashlib.sha256(source.read_bytes()).hexdigest()!=EXPECTED:
 raise SystemExit('O executável de entrada não corresponde à versão usada nesta tradução.')
if not tool.is_file():raise SystemExit('XexTool não encontrado.')
inspect=ROOT/'inspect';inspect.mkdir(exist_ok=True)
destination=inspect/'sm64.xex'
if source!=destination:shutil.copy2(source,destination)
staged_tool=inspect/'xextool/build/XexTool';staged_tool.parent.mkdir(parents=True,exist_ok=True)
if tool!=staged_tool:shutil.copy2(tool,staged_tool)
staged_tool.chmod(staged_tool.stat().st_mode|0o111)
subprocess.run([str(staged_tool),'-b',str(inspect/'base.bin'),str(destination)],check=True)
for script in ['build.py','pack.py','verify.py']:
 subprocess.run([sys.executable,str(ROOT/'ptbr-work'/script)],cwd=ROOT,check=True)
print('Gerado e verificado estaticamente:',ROOT/'sm64-ptbr-teste.xex')
print('É necessário testar no Xbox 360.')
