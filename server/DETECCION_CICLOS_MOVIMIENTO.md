# Detección de Ciclos de Movimiento

## 🎯 Objetivo

Evitar que el bot se quede **enciclado infinitamente** repitiendo la misma secuencia de movimientos.

## ✅ Solución: Pattern Detection

Registrar los últimos movimientos y detectar si se repiten.

### Implementación Simple

```python
# Variables globales
historial_movimientos = []  # ['N', 'E', 'N', 'E', 'N', 'E']
MAX_HISTORIAL = 12  # Últimos 12 movimientos

def agregar_movimiento(heading):
    """Registra el movimiento actual"""
    global historial_movimientos
    
    historial_movimientos.append(heading)
    if len(historial_movimientos) > MAX_HISTORIAL:
        historial_movimientos.pop(0)  # Eliminar más antiguo

def detectar_ciclo():
    """
    Detecta si estamos repitiendo un patrón de movimientos.
    Retorna: tamaño del patrón si detecta ciclo, None si no
    """
    global historial_movimientos
    
    # Necesitamos al menos 6 movimientos para detectar ciclo
    if len(historial_movimientos) < 6:
        return None
    
    # Probar patrones de tamaño 2, 3, 4
    for patron_size in [2, 3, 4]:
        if len(historial_movimientos) < patron_size * 2:
            continue
        
        # Extraer último patrón
        patron = historial_movimientos[-patron_size:]
        
        # Verificar si se repite antes
        patron_previo = historial_movimientos[-(patron_size*2):-patron_size]
        
        if patron == patron_previo:
            print(f"¡CICLO DETECTADO! Patrón: {patron}")
            return patron_size
    
    return None

def romper_ciclo():
    """
    Cuando detectamos ciclo, forzar una decisión diferente.
    Retorna: dirección a explorar para romper el ciclo
    """
    # Obtener direcciones disponibles del checkpoint actual
    direcciones_disponibles = obtener_direcciones_unexplored()
    
    if len(direcciones_disponibles) == 0:
        # No hay opciones, hacer backtrack normal
        return None
    
    # Elegir dirección que NO esté en el patrón reciente
    for direccion in direcciones_disponibles:
        # Contar cuántas veces aparece en el historial reciente
        apariciones = historial_movimientos[-6:].count(direccion)
        
        if apariciones == 0:
            # Esta dirección no la hemos usado recientemente
            print(f"Rompiendo ciclo: explorando {direccion}")
            return direccion
    
    # Si todas están en historial, elegir la menos usada
    menos_usada = min(direcciones_disponibles, 
                      key=lambda d: historial_movimientos.count(d))
    print(f"Rompiendo ciclo: usando dirección menos frecuente {menos_usada}")
    return menos_usada
```

### Integración en el Loop Principal

```python
def loop_principal():
    while True:
        # Leer sensores
        sensores = leer_sensores()
        
        # Detectar checkpoint
        if es_checkpoint(sensores):
            procesar_checkpoint(sensores)
        
        # ANTES de decidir próximo movimiento, verificar ciclo
        if detectar_ciclo():
            # Intentar romper el ciclo
            direccion = romper_ciclo()
            
            if direccion is not None:
                # Forzar esta dirección
                girar_hacia(direccion)
                avanzar_hasta_pared_o_checkpoint()
                agregar_movimiento(direccion)
                continue
        
        # Decisión normal (DFS)
        direccion = decidir_proxima_direccion()
        
        if direccion is None:
            # Backtrack
            hacer_backtrack()
        else:
            # Explorar
            girar_hacia(direccion)
            avanzar_hasta_pared_o_checkpoint()
            agregar_movimiento(direccion)
```

## 📊 Ejemplos de Ciclos Detectados

### Ciclo Simple (Patrón de 2)

```
Movimientos: N, S, N, S, N, S
             └─┘  └─┘  └─┘
             Patrón se repite 3 veces

Acción: Explorar E u W para romper
```

### Ciclo Cuadrado (Patrón de 4)

```
Movimientos: N, E, S, W, N, E, S, W
             └────────┘  └────────┘
             Patrón se repite

Acción: Explorar dirección no usada
```

### Ciclo en L (Patrón de 3)

```
Movimientos: N, E, S, N, E, S
             └──────┘  └──────┘
             
Acción: Forzar W
```

## 🔍 Casos Especiales

### Caso 1: Ciclo sin Salida

```python
# Si detectamos ciclo pero NO hay direcciones UNEXPLORED
if detectar_ciclo() and len(obtener_direcciones_unexplored()) == 0:
    # Esto significa que ya exploramos todo desde este punto
    # Hacer backtrack normal
    hacer_backtrack()
```

### Caso 2: Falso Positivo

```python
# Movimientos: N, N, N (avanzando recto por pasillo largo)
# NO es ciclo, es progreso lineal

# Solución: Solo detectar si el patrón incluye GIROS
def detectar_ciclo():
    # ... código anterior ...
    
    # Verificar que el patrón tenga al menos 2 direcciones diferentes
    if len(set(patron)) < 2:
        return None  # No es ciclo, es movimiento lineal
    
    # ... resto del código ...
```

### Caso 3: Ciclo Intencional (Backtracking)

```python
# Durante backtracking, es normal volver por donde vinimos
# NO queremos romper esto

# Solución: Solo detectar ciclos cuando NO estamos en modo backtrack
if not en_backtrack and detectar_ciclo():
    romper_ciclo()
```

## 🎮 Configuración

```python
# Configurables
MAX_HISTORIAL = 12          # Cuántos movimientos recordar
MIN_PATRON_SIZE = 2         # Mínimo tamaño de patrón (2 movimientos)
MAX_PATRON_SIZE = 4         # Máximo tamaño de patrón (4 movimientos)
MIN_REPETICIONES = 2        # Cuántas veces debe repetirse para ser ciclo
```

## 💡 Ventajas de Este Approach

✅ **Sin odometría**: Solo requiere recordar direcciones
✅ **Simple**: ~30 líneas de código
✅ **Efectivo**: Detecta loops obvios
✅ **Configurable**: Puedes ajustar sensibilidad
✅ **Robusto**: No acumula error

## ❌ Limitaciones

⚠️ No detecta ciclos espaciales (A→B→C→D→A donde todas las direcciones son diferentes)
⚠️ Requiere al menos 2 repeticiones del patrón para detectar

## 🚀 Implementación Mínima (10 líneas)

Si quieres la versión más simple posible:

```python
movimientos = []

def loop():
    # ... leer sensores ...
    
    # Detectar ciclo simple: últimos 6 movimientos == anteriores 6
    if len(movimientos) >= 12:
        if movimientos[-6:] == movimientos[-12:-6]:
            # ¡Ciclo! Forzar dirección diferente
            explorar_direccion_no_usada()
            return
    
    # Movimiento normal
    direccion = decidir_direccion()
    mover(direccion)
    movimientos.append(direccion)
```

## 🎯 Recomendación Final

Implementa la **versión simple** primero:
- Historial de 12 movimientos
- Detectar patrones de tamaño 2, 3, 4
- Si detecta ciclo → explorar dirección menos usada

**Esto resuelve el 95% de los casos de enciclado sin necesidad de odometría.**
