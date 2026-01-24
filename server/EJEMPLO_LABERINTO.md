# Guía de Pruebas - Visualizador de Grafos

Esta es una guía práctica para probar el visualizador del sistema de checkpoints.

---

## 🚀 Inicio Rápido

```bash
cd server
python3 main.py
```

El sistema inicia con:
- ✅ Checkpoint #0 creado (inicio)
- 🧭 Heading por defecto: NORTE (N)
- 🎮 Ventana de visualización con pan/zoom

---

## 📋 Comandos Básicos

### 1. Crear Checkpoints

```
Formato: <HEADING> <front> <left> <right>
HEADING = N, S, E, W (hacia dónde mira el bot)
Estados = UNEXPLORED/UN/U, EXPLORED/EX/E, BLOCKED/BL/B
```

**Ejemplos:**

```bash
# Checkpoint con apertura al este (usando abreviaciones cortas)
> N UN UN BL

# Checkpoint con apertura norte y oeste (nombres completos)
> E UNEXPLORED UNEXPLORED BLOCKED

# Dead-end (todas bloqueadas excepto por donde llegó)
> W BL BL BL
```

### 2. Marcar Dead-end

```bash
> deadend
💀 Checkpoint marcado como dead-end
🔙 Backtracking automático al parent
```

### 3. Actualizar Estados

```bash
# Formato: UPDATE <id> <dirección> <estado>
# Acepta cualquier variante: UN/EX/BL o U/E/B o nombres completos

> UPDATE 2 E EX

> UPDATE 1 N BL

> UPDATE 0 W BLOCKED
```

### 4. Navegación

```bash
# Mover a checkpoint específico
> MOVE 3

# Ver estadísticas
> stats

# Resetear todo
> RESET
```

---

## 🧪 Ejemplos de Pruebas

### Prueba 1: Pasillo Lineal Simple

```bas BL BL
✅ CP#1 creado | N-S conectados

> N UN BL BL  
✅ CP#2 creado | N-S conectados

> N BL BL BLKED  
✅ CP#2 creado | N-S conectados

> N BLOCKED BLOCKED BLOCKED
✅ CP#3 creado (dead-end)
🔙 Backtrack automático a CP#2
```

**Resultado visual:**
```
CP#0 ─ CP#1 ─ CP#2 ─ CP#3 (💀)
```

---

### Prueba 2: Intersección en T

```bash
# Avanzar hasta intersección

> N UN BL BL
✅ CP#1 creado

> N UN UN BL
✅ CP#2 creado (intersección detectada: N y W abiertas)

# Explorar oeste
> W BL BL BL
✅ CP#3 creado (dead-end W)
🔙 Backtrack a CP#2

# Explorar norte
> N BL BL BL
✅ CP#4 creado (dead-end N)
```

**Resultado visual:**
```
        CP#4 (💀)
          │
    CP#3 ─ CP#2
     (💀)  │
         CP#1
          │
         CP#0
```

---

### Prueba 3: Cuadrado/Loop

```bash
> N UN UN BL
✅ CP#1 | N y E abiertos

> E UN BL UN
✅ CP#2 | E y S abiertos

> S UN UN BL
✅ CP#3 | S y W abiertos

> W UN BL UN
✅ CP#4 | W y N abiertos

# Ahora todas las direcciones están exploradas
# El algoritmo haría backtracking
```

**Resultado visual:**
```
CP#1 ─ CP#2
 │      │
CP#4 ─ CP#3
```

---

### Prueba 4: Backtracking Manual

```bash
# Crear algunos checkpoints
> N U B B
> N U B B
> N B B B

# Ahora estás en CP#3 (dead-end), volver manualmente
> MOVE 1

# O hacer backtracking automático
> deadend
```

---

### Prueba 5: Actualizar Estados Durante Exploración

```bash
# Crear checkpoint con norte unexplored
> N UN BL BL
✅ CP#1

# Explorar norte, encontrar pared
> N BL BL BL
✅ CP#2

# Actualizar CP#1 para marcar que norte está bloqueado
> UPDATE 1 N BL

# CP#1 ahora muestra N en rojo (blocked)
```

---

## 🎮 Controles de Cámara

- **Mouse drag**: Pan (mover la vista)
- **Mouse wheel**: Zoom in/out
- **Barra espaciadora**: Centrar en checkpoint actual
- **ESC**: Salir

---

## 🎨 Código de Colores

- 🟢 **Verde**: Checkpoint actual
- 🔵 **Azul**: Checkpoints normales
- 🔴 **Rojo**: Dead-ends
- **Círculos pequeños N/S/E/W**:
  - 🟡 Amarillo = UNEXPLORED
  - 🟢 Verde = EXPLORED
  - 🔴 Rojo = BLOCKED

---

## 📊 Comando `stats`

Muestra información del grafo:

```bash
> stats
📊 === ESTADÍSTICAS DEL GRAFO ===
📍 Total de checkpoints: 8
💀 Dead-ends: 3
🔍 Direcciones sin explorar: 5
🤖 Checkpoint actual: #6
```

---

## 💡 Tips para Pruebas

1. **Empieza simple**: Prueba pasillos rectos antes de intersecciones
2. **Usa MOVE**: Para probar backtracking sin crear checkpoints extra
3. **Verifica estados**: Usa UPDATE para corregir errores
4. **Zoom in/out**: Para ver mejor los indicadores de direcciones
5. **Resetea frecuentemente**: `reset` para empezar prueba nueva

---

## 🐛 Casos de Prueba para Validar Lógica

### ✅ Validar: Dirección de llegada se marca EXPLORED

```bash
> N U B B
# CP#1 creado, debe mostrar S=EXPLORED automáticamente
```

### ✅ Validar: Dead-end hace backtracking automático

```bash
> N U B B    # CP#1
> N B B B    # CP#2 (todas bloqueadas)
> deadend
# Debe volver automáticamente a CP#1
```

### ✅ Validar: Actualización de estados funciona

```bash
> N U U B      # CP#1 con N y W unexplored
> UPDATE 1 W BLOCKED
# W debe cambiar de amarillo a rojo
```

### ✅ Validar: Conexiones bidireccionales

```bash
> N U B B      # CP#0 → CP#1
> MOVE 0       # Volver a CP#0
# Debe mostrar N=EXPLORED
```

---

## 🔧 Depuración

Si algo no funciona:

1. **Verifica heading**: Debe ser N, S, E o W
2. **Verifica estados**: Acepta UNEXPLORED/UN/U, EXPLORED/EX/E, BLOCKED/BL/B
3. **Cuenta parámetros**: Deben ser 4 (heading + 3 estados)
4. **Revisa terminal**: Los mensajes de error indican qué está mal

**Ejemplo de error común:**

```bash
> N U B        # ❌ Faltan parámetros
❌ Comando inválido

> X U B B      # ❌ Heading inválido
❌ Dirección inválida: X

> N MAYBE B B  # ❌ Estado inválido
❌ Estado inválido: MAYBE
   Usa: UNEXPLORED/UN/U, EXPLORED/EX/E, BLOCKED/BL/B
```

---

Esta herramienta sirve para **visualizar y entender** cómo funciona el sistema de grafos antes de implementar el bot real.
