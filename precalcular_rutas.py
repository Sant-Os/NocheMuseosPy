import time
import json
import configuracion
from configuracion import MUSEOS, obtener_ruta_vehiculo

def generar_caches():
    nombres = list(MUSEOS.keys())
    total_museos = len(nombres)
    

    total_pares = total_museos * (total_museos - 1)
    
    print(f"Iniciando pre-cálculo de {total_pares} pares de rutas...")
    
    pares_procesados = 0
    for i in range(total_museos):
        for j in range(total_museos):
            if i == j:
                continue
                
            origen = MUSEOS[nombres[i]]
            destino = MUSEOS[nombres[j]]
            

            print(f"[{pares_procesados+1}/{total_pares}] Calculando Peatón: {nombres[i][:15]}... -> {nombres[j][:15]}...")
            obtener_ruta_vehiculo(origen, destino, perfil="peaton")
            

            print(f"[{pares_procesados+1}/{total_pares}] Calculando Taxi: {nombres[i][:15]}... -> {nombres[j][:15]}...")
            obtener_ruta_vehiculo(origen, destino, perfil="driving")
            
            pares_procesados += 1
            
    print("¡Pre-cálculo finalizado exitosamente!")
    print(f"Rutas peatonales guardadas en: {configuracion.ARCHIVO_PEATONAL}")
    print(f"Rutas vehiculares guardadas en: {configuracion.ARCHIVO_TAXI}")

if __name__ == "__main__":
    generar_caches()
