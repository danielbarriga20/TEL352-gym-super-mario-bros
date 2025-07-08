from typing import List


def make_environment_actions() -> List[List[str]]:
    """
    Esta función debe retornar una lista que contenga
    todas las combinaciones de acciones
    que su agente inteligente podrá utilizar durante la ejecución.
    
    El formato final de actions corresponde a una lista de listas
    en donde cada sublista contendrá posibles acciones
    a realizar en cada baldoza
    
    por ejemplo, la siguiente lista indica que las opciones disponibles
    en cada baldoza son "right" o "left": 
    actions = [["right"], ["left"]]
    
    Acciones disponibles:
    
    "NOOP": no presiona ningún botón
    
    "right": presiona el botón para hacer avanzar a Mario hacia la derecha
    
    "left": presiona el botón para hacer avanzar a Mario hacia la izquierda
    
    "down": presiona el botón para hacer avanzar a Mario hacia abajo
              (útil para entrar en una tubería o para bajar cuando Mario escala)
    
    "up": presiona el botón para hacer avanzar a Mario hacia arriba
              (útil para subir cuando Mario escala)
    
    "A": presiona el botón para hacer saltar a Mario
              Si se presiona durante varios frames consecutivos,
              Mario saltará más alto hasta alcanzar la máxima altura
    
    "B": presiona el botón para hacer correr a Mario
              Se debe presionar consecutivamente
              durante varios frames para notar la diferencia
    
    Es posible presionar más de un botón al mismo tiempo, por ejemplo, la lista
    actions = [["right", "B", "A"]]
    indica que el agente deberá presionar simultáneamente
    los botones "right", "B" y "A"
    
    A partir de aqui construya su lista de acciones permitidas
    
    * Esta lista incluye TODAS las acciones posibles,
    no confundir con la lista de acciones por baldoza    
    """

    # placeholder, reemplazar por lista propia de acciones
    actions = [
        ["NOOP"],                 # 0
        ["right"],                # 1  caminar
        ["right", "B"],           # 2  correr
        ["right", "A"],           # 3  salto corto
        ["right", "A", "B"],      # 4  salto largo corriendo
        ["A"],                    # 5  salto vertical
        ["left"],                 # 6  retroceder
        ["left", "B"],            # 7  retroceder corriendo
        ["down"],                 # 8  agacharse / tubería
        ["right", "A", "A"],      # 9  mantener A 2 frames - salto medio
        ["right", "A", "A", "B"]  # 10 mantener A+B 3 frames - salto alto corriendo
    ]
    return actions 
