#!/usr/bin/env python3
"""
Script de prueba para verificar por qué no se muestra el minimapa
"""

import sys
import os

print("=" * 60)
print("DIAGNÓSTICO DEL MINIMAPA")
print("=" * 60)

# 1. Verificar configuración
print("\n1. VERIFICANDO CONFIGURACIÓN:")
print("-" * 40)
try:
    import config as CFG
    
    # Verificar configuraciones críticas
    configs_to_check = [
        ('DRAW_FOOTER_BOXES', True),
        ('FOOTER_BOX_COUNT', 4),
        ('MINIMAP_BOX_INDEX', None),
        ('FOOTER_TITLES', ['SIMBOLOGÍA', 'MAPA DE UBICACIÓN', '', 'OBSERVACIONES'])
    ]
    
    for config_name, expected in configs_to_check:
        if hasattr(CFG, config_name):
            value = getattr(CFG, config_name)
            print(f"✓ {config_name} = {value}")
            if config_name == 'MINIMAP_BOX_INDEX' and value == -1:
                print("  ⚠️  MINIMAP_BOX_INDEX = -1 significa que el minimapa está DESACTIVADO")
            elif config_name == 'MINIMAP_BOX_INDEX' and value is None:
                print("  ❌ MINIMAP_BOX_INDEX no está definido - el minimapa NO se dibujará")
        else:
            print(f"❌ {config_name} NO ESTÁ DEFINIDO en config.py")
            if config_name == 'MINIMAP_BOX_INDEX':
                print("  ❌ Sin MINIMAP_BOX_INDEX, el minimapa NO se dibujará")
    
except ImportError as e:
    print(f"❌ Error al importar config.py: {e}")

# 2. Verificar cartopy
print("\n2. VERIFICANDO CARTOPY:")
print("-" * 40)
try:
    import cartopy
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    print(f"✓ Cartopy instalado - versión {cartopy.__version__}")
    print("✓ Módulos necesarios disponibles (crs, feature)")
except ImportError as e:
    print(f"❌ Cartopy NO está instalado: {e}")
    print("  Para instalar cartopy, ejecute:")
    print("  pip install cartopy")
    print("  o")
    print("  conda install -c conda-forge cartopy")

# 3. Verificar otras dependencias
print("\n3. VERIFICANDO OTRAS DEPENDENCIAS:")
print("-" * 40)
dependencies = ['numpy', 'matplotlib']
for dep in dependencies:
    try:
        module = __import__(dep)
        version = getattr(module, '__version__', 'versión desconocida')
        print(f"✓ {dep} instalado - versión {version}")
    except ImportError:
        print(f"❌ {dep} NO está instalado")

# 4. Resumen y solución
print("\n" + "=" * 60)
print("RESUMEN Y SOLUCIÓN:")
print("=" * 60)

problems = []
solutions = []

# Verificar problemas de configuración
try:
    import config as CFG
    if not hasattr(CFG, 'MINIMAP_BOX_INDEX'):
        problems.append("MINIMAP_BOX_INDEX no está definido en config.py")
        solutions.append("Agregar 'MINIMAP_BOX_INDEX = 1' en config.py")
    elif getattr(CFG, 'MINIMAP_BOX_INDEX', -1) == -1:
        problems.append("MINIMAP_BOX_INDEX está desactivado (valor = -1)")
        solutions.append("Cambiar 'MINIMAP_BOX_INDEX = -1' a 'MINIMAP_BOX_INDEX = 1' en config.py")
except:
    problems.append("No se puede importar config.py")
    solutions.append("Verificar que config.py existe y es válido")

# Verificar cartopy
try:
    import cartopy
except ImportError:
    problems.append("Cartopy no está instalado")
    solutions.append("Instalar cartopy con: pip install cartopy")

if problems:
    print("\n❌ PROBLEMAS ENCONTRADOS:")
    for i, problem in enumerate(problems, 1):
        print(f"  {i}. {problem}")
    
    print("\n✅ SOLUCIONES:")
    for i, solution in enumerate(solutions, 1):
        print(f"  {i}. {solution}")
else:
    print("\n✅ Todo parece estar configurado correctamente.")
    print("   El minimapa debería aparecer en la segunda caja del footer")
    print("   (MAPA DE UBICACIÓN) cuando ejecute main.py")

print("\n" + "=" * 60)
print("Para ejecutar el programa principal: python3 main.py")
print("=" * 60)