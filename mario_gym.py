from nes_py.wrappers import JoypadSpace
import gym_super_mario_bros


def run_simulation(args, map_actions, env_actions, pixel2baldoza):
    env = gym_super_mario_bros.make('SuperMarioBros-v0')
    env = JoypadSpace(env, env_actions)

    done = True
    info = {
        "coins": 0,
        "flag_get": False,
        "life": 2,
        "score": 0,
        "stage": 1,
        "status": "dead",
        "time": 400,
        "world": 1,
        "x_pos": 1,
        "y_pos": 79
    }

    results = {
        "info": info,
    }

    x_pos = 0
    count = 0

    # NUEVO: Lista para almacenar las acciones tomadas en esta simulación
    actions_taken_in_run = [] 
    
    for step in range(args.n_frames):
        if done:
            state = env.reset()

        n_lives = info["life"]
        action_idx = 0
        n_baldoza = pixel2baldoza(info["x_pos"], info["status"])
        
        try:
            action_idx = map_actions[n_baldoza]
            if not (0 <= action_idx < len(env_actions)):
                action_idx = env_actions.index(["NOOP"])
            
            # NUEVO: Almacena la acción tomada (su índice)
            actions_taken_in_run.append(action_idx) 

        except IndexError:
            action_idx = env_actions.index(["NOOP"])
            results["info"]["status"] = "error"
            # NUEVO: Almacena la acción por defecto si hay un error de índice
            actions_taken_in_run.append(action_idx) 
            #print(f"--- Mario fuera del rango de acciones definidas en Baldosa: {n_baldoza} (X_pos: {info['x_pos']}). Fin de simulación. ---")
            break 
        except Exception as e:
            action_idx = env_actions.index(["NOOP"])
            results["info"]["status"] = "error"
            # NUEVO: Almacena la acción por defecto si hay un error inesperado
            actions_taken_in_run.append(action_idx) 
            #print(f"--- Error inesperado al seleccionar acción para baldoza {n_baldoza}: {e}. Fin de simulación. ---")
            break

        state, reward, done, info = env.step(action_idx)

        if info["life"] < n_lives:
            results["info"]["status"] = "dead"
            print(f"--- Mario murió en Baldosa: {n_baldoza} (X_pos: {info['x_pos']}) ---")
            break

        if info["x_pos"] == x_pos:
                if count >= 100:
                    results["info"]["status"] = "dead end"
                    break
                else:
                    count += 1
        else:
            count = 0
            x_pos = info["x_pos"]
        results["info"] = info

        if done or info["flag_get"]:
            print(f"--- Simulación finalizada: Bandera obtenida: {info['flag_get']} en Baldosa: {n_baldoza} (X_pos: {info['x_pos']}) ---")
            break

        if args.render:
            env.render()

    env.close()

    # MODIFICADO: Retorna tanto la info como las acciones tomadas
    return results["info"], actions_taken_in_run