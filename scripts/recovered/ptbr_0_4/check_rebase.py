"""Compare mapped images: old build, user-corrected build, translated build.
Usage: python3 check_rebase.py old-base.bin corrected-base.bin translated-base.bin
"""
from pathlib import Path
import hashlib,json,struct,sys
if len(sys.argv)!=4:raise SystemExit(__doc__)
paths=[Path(x) for x in sys.argv[1:]]
old,new,translated=[p.read_bytes() for p in paths]
assert len(old)==len(new)==len(translated)
pe=struct.unpack_from('<I',new,60)[0]
sect=pe+24+struct.unpack_from('<H',new,pe+20)[0]
fields={}
for n in range(struct.unpack_from('<H',new,pe+6)[0]):
 at=sect+n*40
 fields[new[at:at+8].split(b'\0')[0]]=at
size_field=fields[b'.text']+8
allowed=set(range(size_field,size_field+4))
fix_changes=0;translation_changes=0;intersections=[]
for i,(a,b,c) in enumerate(zip(old,new,translated)):
 if a!=b:fix_changes+=1
 if b!=c:translation_changes+=1
 if a!=b and b!=c:
  assert i in allowed,('Corrected-build change overwritten',hex(i))
  intersections.append(i)
result={
 'status':'PASS - alteracoes da base corrigida preservadas',
 'scope':'Comparacao estatica das imagens mapeadas; sem teste do canhao em execucao.',
 'old_mapped_sha256':hashlib.sha256(old).hexdigest(),
 'corrected_mapped_sha256':hashlib.sha256(new).hexdigest(),
 'translated_mapped_sha256':hashlib.sha256(translated).hexdigest(),
 'changed_bytes_old_to_corrected':fix_changes,
 'changed_bytes_corrected_to_translated':translation_changes,
 'overlaps':[hex(i) for i in intersections],
 'overlap_explanation':'Somente VirtualSize da secao PE .text, ampliado para as rotinas de texto; nao sao instrucoes do jogo.',
 'all_other_corrected_build_differences_preserved':True}
(Path(__file__).parent/'preservacao-base-corrigida.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
