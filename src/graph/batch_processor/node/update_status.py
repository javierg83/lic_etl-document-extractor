from src.utils.db import get_db_connection
from src.constants.states import LicitacionStatus

class UpdateLicitacionStatusNode:
    @staticmethod
    def execute(state: dict) -> dict:
        try:
            return UpdateLicitacionStatusNode._run(state)
        except Exception as e:
            # Si falla actualizar estado, no deberíamos detener todo, pero loggeamos
            print(f"❌ Error en UpdateLicitacionStatusNode: {e}")
            state["error_node"] = "update_licitacion_status"
            state["error"] = str(e)
            return state

    @staticmethod
    def _run(state: dict) -> dict:
        licitacion_id = state.get("licitacion_id")
        target_status = state.get("target_licitacion_status") # El grafo debe setear esto antes de llamar
        
        if not licitacion_id or not target_status:
            print("⚠️ UpdateLicitacionStatusNode: Faltan datos (licitacion_id o target_status).")
            return state
            
        print(f"🔄 [Batch] Actualizando Licitación {licitacion_id} a estado '{target_status}'...")
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                tipo_adquisicion = state.get("tipo_adquisicion")
                
                if tipo_adquisicion:
                    query = """
                        UPDATE licitaciones 
                        SET estado = %s, tipo_licitacion = %s
                        WHERE id = %s
                    """
                    cursor.execute(query, (target_status, tipo_adquisicion, licitacion_id))
                else:
                    query = """
                        UPDATE licitaciones 
                        SET estado = %s 
                        WHERE id = %s
                    """
                    cursor.execute(query, (target_status, licitacion_id))
                    
                conn.commit()
            print(f"✅ [Batch] Estado actualizado a '{target_status}'.")
        except Exception as e:
            print(f"❌ Error SQL actualizando estado de licitación: {e}")
            raise e
        finally:
            conn.close()
            
        return state
