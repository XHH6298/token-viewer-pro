# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('static', 'static'), ('icon.ico', '.'), ('icon.png', '.')]
binaries = []
hiddenimports = []

# FastAPI / Uvicorn
hiddenimports += [
    'uvicorn.loops.auto', 'uvicorn.loops.asyncio',
    'uvicorn.protocols.http.auto', 'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.websockets.auto', 'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.lifespan.on', 'uvicorn.lifespan.off',
    'uvicorn.middleware.proxy_headers', 'uvicorn.middleware.wsgi',
    'starlette', 'starlette.applications', 'starlette.requests',
    'starlette.responses', 'starlette.routing', 'starlette.middleware',
    'starlette.middleware.errors', 'starlette.background', 'starlette.datastructures',
    'starlette.types', 'starlette.concurrency', 'starlette.websockets',
    'anyio', 'anyio._backends._asyncio', 'anyio._core._asyncio_selector_thread',
    'pydantic', 'pydantic_core', 'httptools', 'h11', 'click', 'yaml', 'wsgiref',
    'multipart', 'python_multipart', 'itsdangerous', 'email_validator',
]

# pywebview
tmp_ret = collect_all('pywebview')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

excludes = [
    'numpy', 'scipy', 'pandas', 'matplotlib', 'PIL', 'torch', 'sklearn',
    'tensorflow', 'IPython', 'notebook', 'bokeh', 'plotly',
    'PyQt5', 'PyQt6', 'PySide2', 'PySide6', 'gi', 'cefpython3',
    'trio', 'uvloop', 'watchfiles', 'websockets.sync',
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TokenViewerPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    manifest='app.manifest',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='TokenViewerPro',
)
