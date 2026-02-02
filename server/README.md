# MazeRunner - Editor Simple de Laberinto

Editor de laberinto minimalista con sistema de cuadrícula y numeración de camino.

## 🎯 Características

- **Sistema simple**: Un solo archivo, sin complejidades
- **Dos estados de pared**: Bloqueada (negro) o Abierta (sin pared)
- **Bordes grises**: Los bordes exteriores son grises automáticamente
- **Numeración de camino**: Marca celdas con 1, 2, 3... para definir la ruta
- **Generación de código**: Output compatible con el sistema de grid del bot

## 🚀 Instalación

```bash
pip install pygame
```

## 📖 Uso

```bash
cd server
python3 maze_editor.py
```

1. Ingresa el tamaño de la cuadrícula (filas x columnas)
2. Clic en paredes para toggle bloqueada/abierta
3. Clic en celdas para numerarlas (orden del camino)
4. Clic derecho para quitar número
5. Presiona `P` o usa el botón para generar código

## ⌨️ Controles

| Acción | Control |
|--------|---------|
| Toggle pared | Clic izquierdo en pared |
| Numerar celda | Clic izquierdo en celda |
| Numerar múltiples | Mantener y arrastrar en celdas |
| Quitar número | Clic derecho en celda |
| Rotar orientación | `Q` (antihorario) / `E` (horario) |
| Generar código | `P` o botón |
| Limpiar números | `C` |
| Reset todo | `R` |
| Salir | `ESC` |

## 🧭 Orientación Cardinal

Controla qué dirección del grid visual corresponde a cada dirección cardinal (N/S/E/W):

- **0° (Norte ↑)**: Arriba = Norte (por defecto)
- **90° (Este →)**: Derecha = Norte
- **180° (Sur ↓)**: Abajo = Norte  
- **270° (Oeste ←)**: Izquierda = Norte

Usa `Q`/`E` para rotar. La brújula visual muestra la orientación actual.

## 📦 Output

El código generado tiene el formato de **grafos con direcciones cardinales**:

```python
RUTA = [
    (0, 'N', 1),
    (1, 'N', 2),
    (2, 'N', 3),
    (3, 'N', 4),
    (4, 'E', 5),
    (5, 'E', 6),
]

ESTADOS = {
    0: {'N': 'EX', 'S': 'BL', 'E': 'BL', 'W': 'BL'},
    1: {'N': 'EX', 'S': 'EX', 'E': 'EX', 'W': 'BL'},
    2: {'N': 'EX', 'S': 'EX', 'E': 'BL', 'W': 'BL'},
    3: {'N': 'EX', 'S': 'EX', 'E': 'EX', 'W': 'BL'},
    4: {'N': 'BL', 'S': 'EX', 'E': 'EX', 'W': 'BL'},
    5: {'N': 'BL', 'S': 'BL', 'E': 'EX', 'W': 'EX'},
    6: {'N': 'BL', 'S': 'EX', 'E': 'EX', 'W': 'EX'},
}
```

Donde:
- **RUTA**: Lista de tuplas `(checkpoint_origen, dirección, checkpoint_destino)`
- **ESTADOS**: Diccionario de checkpoints con sus 4 direcciones cardinales
  - `'BL'` = Bloqueado (pared física)
  - `'EX'` = Explorado/Libre (sin pared)

## 🎨 Colores

- **Gris**: Bordes exteriores (fijos)
- **Negro**: Paredes internas bloqueadas
- **Blanco**: Celdas normales
- **Azul claro**: Celdas numeradas (camino)

## 📁 Estructura

```
server/
├── maze_editor.py          # Archivo único - todo el sistema
├── requirements.txt        # pygame
└── README.md              # Esta documentación
```

## 🔧 Código

Todo en un solo archivo modular:

```
maze_editor.py
├── Config          # Configuración (colores, tamaños)
├── Cardinal        # Enum de direcciones
├── Cell            # Celda individual
├── Grid            # Sistema de cuadrícula
├── Interaction     # Manejo de mouse
├── Renderer        # Dibujado
├── MazeEditor      # Aplicación principal
└── main()          # Entry point
```

## 💡 Notas

- Sistema simplificado comparado con versiones anteriores
- Sin cámara, sin zoom, sin pan
- Enfocado en crear y exportar laberintos rápidamente
- Compatible con matrix_generator.py del bot
- **Sistema de orientación**: Permite definir qué dirección del grid es Norte
- El bot comenzará mirando a la dirección del primer movimiento en RUTA
