# Guía de Uso - MazeRunner Graph Visualizer

## 🚀 Instalación

```bash
cd server
pip3 install -r requirements.txt
```

## ▶️ Ejecutar

```bash
python3 main.py
```

Se abrirá una ventana de PyGame mostrando el grafo. La consola estará lista para recibir comandos.

## 📚 Ejemplos de Exploración

### Ejemplo 1: Pasillo Simple con Giro

```
Estado inicial: Checkpoint #0, mirando al NORTE

┌─────────────────┐
│                 │
│    [START]      │  ← Paredes a los lados
│       ↑         │
│       N         │
│                 │
└─────────────────┘

Comando: N UNEXPLORED BLOCKED BLOCKED
Explicación: Avanza al norte, frente abierto, laterales bloqueados
```

**Resultado**: Se crea Checkpoint #1 al norte de #0

```
Siguiente estado: En Checkpoint #1, mirando al NORTE
Frente bloqueado, derecha abierta

Comando: E UNEXPLORED BLOCKED UNEXPLORED
Explicación: Gira al este, nuevo camino a la derecha
```

**Resultado**: Se crea Checkpoint #2 al este de #1

### Ejemplo 2: Intersección (4 Direcciones)

```
Estado: Checkpoint #5, llegaste desde el OESTE

      [NORTH]
          │
          │
[WEST]─[CP#5]─[EAST]
          │
          │
      [SOUTH]

Comando: N UNEXPLORED UNEXPLORED UNEXPLORED
Explicación: Decides explorar al norte, las otras direcciones quedan marcadas como UNEXPLORED
```

### Ejemplo 3: Dead-End

```
Estado: Llegaste a un callejón sin salida

Comando: N BLOCKED BLOCKED BLOCKED
```

El checkpoint se creará con 3 direcciones bloqueadas + 1 explorada (por donde llegaste).

```
Luego marca como dead-end:
Comando: deadend
```

### Ejemplo 4: Backtracking

```
Situación: Estás en Checkpoint #7, todas las direcciones ya exploradas o bloqueadas

Comando: move 5
Explicación: Vuelves al Checkpoint #5 que aún tiene direcciones UNEXPLORED
```

## 🎯 Comandos Completos

### Crear Checkpoint
```
<DIRECCION> <FRONT> <LEFT> <RIGHT>

Direcciones: N, S, E, W
Estados: UNEXPLORED, EXPLORED, BLOCKED (o U, E, B)

Ejemplos:
N UNEXPLORED BLOCKED BLOCKED
S BLOCKED U U
E U B U
```

### Actualizar Checkpoint Existente
```
update <checkpoint_id> <direccion> <estado>

Ejemplo:
update 3 N BLOCKED
update 5 E EXPLORED
```

### Navegación
```
move <checkpoint_id>     # Mover a checkpoint específico
stats                    # Ver estadísticas
deadend                  # Marcar actual como dead-end
reset                    # Reiniciar todo
quit                     # Salir
```

## 🎨 Interpretación Visual

### Checkpoint Actual (Amarillo)
```
      🟡
      │
      │
```

### Indicadores de Direcciones
```
    🟡 (N - UNEXPLORED)
     │
🔴 ─ ⚪ ─ 🟢
(W)  CP  (E)
     │
    🔴
   (S - BLOCKED)
```

- 🟡 Amarillo: No explorado
- 🟢 Verde: Explorado (hay conexión)
- 🔴 Rojo: Bloqueado (pared)

### Conexiones
Las líneas grises conectan checkpoints que tienen EXPLORED en sus direcciones.

## 📖 Escenario Completo de Prueba

```bash
# Iniciar en Checkpoint #0, mirando Norte
> N U B B          # Avanza norte, pasillo con paredes laterales
✅ Checkpoint #1 creado

> N U B B          # Sigue al norte
✅ Checkpoint #2 creado

> E U U B          # Gira al este, camino abierto adelante y a la izquierda
✅ Checkpoint #3 creado

> N B B U          # Gira al norte, frente bloqueado, derecha abierta
✅ Checkpoint #4 creado

> deadend          # Es un dead-end
🚫 Checkpoint #4 marcado como dead-end

> move 3           # Volver a checkpoint #3 que tiene direcciones sin explorar
🤖 Movido a Checkpoint #3

> N U U B          # Explorar al norte
✅ Checkpoint #5 creado

> stats            # Ver estadísticas
📊 ESTADÍSTICAS:
   Total checkpoints: 6
   Dead-ends: 1
   Direcciones sin explorar: X
   Exploración completa: ❌ NO
```

## 🐛 Troubleshooting

**Error: pygame not installed**
```bash
pip3 install pygame
```

**La ventana no responde**
- Los comandos se ingresan en la **consola**, no en la ventana de PyGame
- La ventana es solo para visualización

**No veo los indicadores de direcciones**
- Haz zoom in con el scroll del mouse
- Los indicadores solo se muestran cuando zoom > 0.6x

**Quiero centrar la vista en el bot**
- Presiona **Espacio** en la ventana de PyGame
- O escribe: `move <id_checkpoint_actual>`

## 💡 Tips

1. **Exploración sistemática**: Sigue el patrón N-E-W-S para elegir direcciones UNEXPLORED
2. **Backtracking**: Usa `move` para volver a checkpoints con UNEXPLORED
3. **Visualización**: Usa zoom y pan para navegar por el grafo completo
4. **Reset**: Si algo sale mal, usa `reset` para empezar de nuevo

## 🔗 Próximos Pasos

Una vez que el bot esté programado:
1. El bot enviará comandos automáticamente vía HTTP
2. El server procesará los checkpoints en tiempo real
3. La visualización se actualizará automáticamente
