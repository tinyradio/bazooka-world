#!/usr/bin/env python3
"""
index.html 안의 모든 로컬 에셋(assets/...)을 base64 data URI로 인라인해서
어디서 더블클릭(file://)해도 동작하는 자체완결 HTML을 생성한다.

사용법:  python3 build-standalone.py
출력:    bazooka-standalone.html
"""
import base64
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "index.html"
OUT = ROOT / "bazooka-standalone.html"

MIME = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".glb": "model/gltf-binary",
    ".webp": "image/webp",
}

html = SRC.read_text(encoding="utf-8")

# 캐시버스터(?v=N) 제거 — data URI 뒤에 붙으면 URI가 깨진다
html = re.sub(r"(assets/[A-Za-z0-9_./-]+\.(?:jpg|jpeg|png|svg|glb|webp))\?v=\d+", r"\1", html)

# index.html 안에서 참조하는 모든 로컬 에셋 경로를 수집
paths = sorted(set(re.findall(r"assets/[A-Za-z0-9_./-]+\.(?:jpg|jpeg|png|svg|glb|webp)", html)))

total_in = 0
for rel in paths:
    f = ROOT / rel
    if not f.exists():
        print(f"  ! 누락: {rel} (건너뜀)")
        continue
    data = f.read_bytes()
    total_in += len(data)
    mime = MIME[f.suffix.lower()]
    uri = f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
    # 따옴표로 둘러싸인 정확한 경로 문자열만 교체 (CSS url(), img src, JS 문자열 모두 커버)
    html = html.replace(rel, uri)
    print(f"  + {rel:32s} {len(data)/1024:7.1f} KB")

OUT.write_text(html, encoding="utf-8")
print(f"\n인라인한 에셋 {len(paths)}개 · 원본 {total_in/1024/1024:.2f} MB")
print(f"생성 완료: {OUT}  ({OUT.stat().st_size/1024/1024:.2f} MB)")
