import os
import random
from typing import List
import copy

import cloudpickle
import datetime

from acciones import make_environment_actions
from mario_gym import run_simulation
from pixel2cell import conversion_pixel_baldoza


class SuperMarioAgenteTEL:
    def __init__(self, args):
        self.args = args

        self.actions = self.make_environment_actions()

        # Atributos para VNS
        self.k_max = 3  # Número máximo de estructuras de vecindario
        self.current_solution = self.generate_initial_solution() #map_actions
        self.current_results = self.make_results(self.current_solution)
        self.last_death_tile = None

        self.best_map_actions = copy.deepcopy(self.current_solution)
        self.best_map_actions_results = copy.deepcopy(self.current_results)
        self.best_eval_score = self.eval_actions(self.best_map_actions_results)

        self.historic_map_actions = []
        self.historic_results = []
        self.iterations_without_improvement = 0
        self.max_iterations_without_improvement = 350 # Criterio de término

    def conversion_pixel_baldoza(self, n_pixel: int, mario_status: str) -> int:
        return conversion_pixel_baldoza(n_pixel, mario_status)

    def make_environment_actions(self) -> List[List[str]]:
        return make_environment_actions()

    def save_simulation_results(self):
        time_now = datetime.datetime.now()
        time_now = time_now.strftime("%Y_%m_%d_%H_%M_%S")

        backup_data = {
            "historic_actions": self.historic_map_actions,
            "historic_results": self.historic_results,
            "best_actions": self.best_map_actions,
            "best_results": self.best_map_actions_results,
        }

        backup_file_name = f"{time_now}_simulation_results.pkl"
        outdir = "outputs/"
        os.makedirs(outdir, exist_ok=True)

        with open(f"{outdir}/{backup_file_name}", mode="wb") as file:
            cloudpickle.dump(backup_data, file)

    def run_simulation(self, map_actions):
        return run_simulation(
            self.args,
            map_actions,
            self.make_environment_actions(),
            self.conversion_pixel_baldoza,
        )

    def generate_initial_solution(self):
        """
        Genera una solución inicial simple: solo avanzar a la derecha.
        El largo del mapa es variable, pero para este caso se considera un máximo
        de baldosas a explorar para que el agente no intente calcular acciones para baldosas
        que están demasiado lejos del alcance inicial de Mario.
        """
        # Consideramos un número arbitrario de baldosas que Mario podría alcanzar
        # en una simulación para inicializar el mapa de acciones.
        # El nivel 1-1 tiene un ancho de alrededor de 4000 píxeles, lo que da unas 250 baldosas.
        # Se establece un límite superior para evitar soluciones excesivamente grandes.
        max_baldozas_in_level = 220
        
        return [2]* max_baldozas_in_level

    def make_results(self, map_actions):
        """
        No modificar
        Esta función solo ejecuta el run_simulations para generar los resultados
        a partir del map_actions generado por el agente
        En esta función se explican los contenidos de los resultados
        puede ser útil al momento de decidir un criterio de evaluación para su agente
        """
        # MODIFICADO: Recibe tanto la info como las acciones_tomadas
        results_info, actions_taken = self.run_simulation(map_actions)
         # ───── NUEVO: calcula y guarda la baldosa final ─────
        final_tile = self.conversion_pixel_baldoza(
            results_info["x_pos"],
            results_info["status"]
        )
        results_info["final_tile"] = final_tile       # queda disponible para tu lógica
        print(f"🟩  Baldosa final de la simulación: {final_tile}")
        # ────────────────────────────────────────────────────

        if results_info['status'] == 'dead':
            self.last_death_tile = self.conversion_pixel_baldoza(
                results_info['x_pos'], results_info['status']
    )
 
        
        # Opcional: Imprime las acciones tomadas aquí mismo
        # Puedes imprimir solo si es la mejor solución actual, o si es una muerte temprana, etc.
        # Por ahora, las imprimiremos siempre para depuración
        #print(f"Acciones usadas en esta simulación ({len(actions_taken)} pasos):")
        
        print("-" * 50) # Separador

        # Si quieres almacenar las acciones tomadas junto con los resultados para análisis posterior:
        results_info['actions_taken'] = actions_taken

        return results_info # Ahora results_info contiene también 'actions_taken'

    
    def eval_actions(self, results):
        score = 0

        if results["flag_get"]: # Si Mario llega a la bandera, es un éxito [cite: 73]
            score += 1000000 # Gran recompensa por completar el nivel
            score += results["time"] * 100 # Recompensar el tiempo restante [cite: 54]
            score += results["coins"] * 10 # Recompensar monedas [cite: 56]
            score += results["score"] # Recompensar puntaje total [cite: 55]
        else:
            # Recompensa por progreso horizontal. Cuanto más a la derecha, mejor. 
            score += results["x_pos"] * 50 # Multiplicador aumentado para x_pos

            # Penalización por errores tempranos o muerte. 
            if results["status"] == "dead" or results["status"] == "error":
                # Penalización base: cuanto más tiempo transcurre antes de morir, menor el castigo 
                penalty = (400 - results["time"]) * 1000 # Penalización base aumentada

                # **Ajuste clave: Penalización adicional específica para la zona del Goomba**
                # El primer Goomba aparece alrededor de X_pos 280-300 (baldosa ~18-19)
                if results["x_pos"] < 50: # Si muere extremadamente temprano (ej. en el punto de inicio o se cae de inmediato)
                    penalty += (50 - results["x_pos"]) * 2000 # Penalización muy, muy alta
                elif results["x_pos"] < 320: # Si muere antes de X_pos 320 (cubre la zona del primer Goomba y el siguiente agujero)
                    penalty += (320 - results["x_pos"]) * 500 # Penalización significativa para esta zona crítica
                
                score -= penalty
            else: # Si no está muerto y no ha llegado a la bandera
                # Recompensa por cada frame que permanece vivo y avanza
                score += (400 - results["time"]) * 20 
                # Podrías añadir una pequeña recompensa por `y_pos` si subir (saltar) fuera bueno, pero `x_pos` es dominante.
        return score

    def update_best_map_action(self, map_actions, results):
        current_eval_score = self.eval_actions(results)

        if current_eval_score > self.best_eval_score:
            self.best_map_actions = copy.deepcopy(map_actions)
            self.best_map_actions_results = copy.deepcopy(results)
            self.best_eval_score = current_eval_score
            self.iterations_without_improvement = 0 # Resetear contador de no mejora
        else:
            self.iterations_without_improvement += 1

    def criterio_de_termino(self):
        """
        Define el criterio de término para VNS.
        Termina si se alcanza el número máximo de pasos de entrenamiento,
        si se encuentra la bandera, o si no hay mejora después de N iteraciones.
        """
        if self.args.n_training_steps is not None and self.args.current_step >= self.args.n_training_steps:
            print(f"Criterio de término: Alcanzado el número máximo de pasos de entrenamiento ({self.args.n_training_steps}).")
            return True
        if self.best_map_actions_results["flag_get"]: # Ensure this line has correct indentation
            print("Criterio de término: ¡Bandera alcanzada!")
            return True
        if self.iterations_without_improvement >= self.max_iterations_without_improvement:
            print(f"Criterio de término: No hay mejora en {self.max_iterations_without_improvement} iteraciones.")
            return True
        return False

    def shake(self, solution, k):
        shaked = solution[:]
        if self.last_death_tile is None:
            center = random.randint(0, len(shaked)-1)
        else:
            center = self.last_death_tile
        # radio de vecindario proporcional a k
        radius = {1:2, 2:5, 3:12}.get(k,3)
        start = max(0, center - radius)
        end   = min(len(shaked), center + radius + 1)

        for i in range(start, end):
            if random.random() < 0.6:                # prob. de cambiar
                shaked[i] = random.randint(0, len(self.actions)-1)
        return shaked


    def local_search(self, solution):
        best = solution[:]
        best_eval = self.eval_actions(self.make_results(best))

        for _ in range(20):
            a = random.randint(0, len(solution)-4)
            b = a + random.randint(2,4)
            cand = best[:]
            # reasigna el bloque [a:b)
            cand[a:b] = [random.randint(0, len(self.actions)-1) for _ in range(b-a)]
            cand_eval = self.eval_actions(self.make_results(cand))
            if cand_eval > best_eval:
                best, best_eval = cand, cand_eval
        return best

    
    def generate_random_solution(self):
        """
        Genera una solución donde cada baldosa tiene una acción aleatoria.
        """
        max_baldozas_in_level = 300 # Debe ser el mismo que en generate_initial_solution
        random_map_actions = [random.randint(0, len(self.actions) - 1) for _ in range(max_baldozas_in_level)]
        return random_map_actions

    def train(self):
        self.args.current_step = 0 

        print("Iniciando entrenamiento de VNS...")

        while not self.criterio_de_termino():
            k = 1
            local_improvement_found = False # Flag para saber si local_search encontró una mejora
            while k <= self.k_max:
                print(f"Iteración {self.args.current_step}, Vecindario k={k}")

                candidate_solution_shaked = self.shake(self.current_solution, k)
                candidate_solution_local_search = self.local_search(candidate_solution_shaked)
                candidate_results_local_search = self.make_results(candidate_solution_local_search) # Esto imprimirá las acciones

                current_eval = self.eval_actions(self.current_results)
                candidate_eval = self.eval_actions(candidate_results_local_search)

                print(f"  Evaluación actual (current_solution): {current_eval}")
                print(f"  Evaluación de candidato (shake + LS): {candidate_eval}")

                if candidate_eval > current_eval:
                    self.current_solution = copy.deepcopy(candidate_solution_local_search)
                    self.current_results = copy.deepcopy(candidate_results_local_search)
                    self.update_best_map_action(self.current_solution, self.current_results)
                    k = 1  # Reiniciar con el primer vecindario
                    local_improvement_found = True # Se encontró una mejora en esta iteración k
                    print(f"  MEJORA ENCONTRADA! Nueva evaluación: {self.best_eval_score}. Reiniciando k.")
                else:
                    k += 1  # Mover al siguiente vecindario
                    print(f"  No hay mejora en el vecindario k={k-1}. Pasando al siguiente.")
            
            # IMPORANTE: Si después de probar todos los vecindarios (k hasta k_max)
            # no se encontró ninguna mejora que nos hiciera reiniciar k a 1,
            # la solución actual puede estar atascada.
            # En este caso, realizaremos un "Gran Salto" o reiniciaremos current_solution
            # para escapar del óptimo local o la solución estancada.
            if not local_improvement_found:
                print(f"  Después de explorar todos los vecindarios (hasta k={self.k_max}), no se encontró ninguna mejora. Realizando un salto grande.")
                # Opción 1: Re-agitar la mejor solución global hasta el momento con un k muy grande
                # self.current_solution = self.shake(self.best_map_actions, self.k_max + 1) # Crear un k_max+1 en shake para esto
                # self.current_results = self.make_results(self.current_solution)

                # Opción 2 (más simple por ahora): Re-inicializar a una solución aleatoria diferente
                # Generar una nueva solución de base para que VNS no se quede atascado
                print("  Re-inicializando la solución actual a una aleatoria para forzar la exploración.")
                self.current_solution = self.generate_random_solution() # NUEVA FUNCIÓN NECESARIA
                self.current_results = self.make_results(self.current_solution)
                self.update_best_map_action(self.current_solution, self.current_results) # Actualizar por si acaso esta random es buena


            self.historic_map_actions.append(copy.deepcopy(self.current_solution))
            self.historic_results.append(copy.deepcopy(self.current_results))
            self.args.current_step += 1
            print(f"Mejor evaluación hasta ahora: {self.best_eval_score}")

        self.save_simulation_results()
        print("Entrenamiento VNS finalizado.")
        print(f"Mejor evaluación final: {self.best_eval_score}")
        print(f"Bandera obtenida: {self.best_map_actions_results['flag_get']}")
        print(f"Posición X final: {self.best_map_actions_results['x_pos']}")
        
        if self.best_map_actions_results['status'] == 'dead' or \
           self.best_map_actions_results['status'] == 'error':
            final_baldoza_best_solution = self.conversion_pixel_baldoza(
                self.best_map_actions_results['x_pos'], 
                self.best_map_actions_results['status']
            )
            print(f"La mejor solución terminó en Baldosa: {final_baldoza_best_solution} (Status: {self.best_map_actions_results['status']})")
        else:
            final_baldoza_best_solution = self.conversion_pixel_baldoza(
                self.best_map_actions_results['x_pos'], 
                self.best_map_actions_results['status']
            )
            print(f"La mejor solución finalizó en Baldosa: {final_baldoza_best_solution} (Status: {self.best_map_actions_results['status']})")