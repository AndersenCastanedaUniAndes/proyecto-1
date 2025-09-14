import jwt, sys
from jose import __version__ as jose_version

print("🔎 Verificando librerías JWT...")
print("PyJWT module path:", jwt.__file__)
print("PyJWT version:", getattr(jwt, '__version__', 'unknown'))
print("python-jose version:", jose_version)
print("Python version:", sys.version)
