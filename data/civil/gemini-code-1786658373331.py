import subprocess
import webbrowser
import time

def desplegar_sistema():
    print("🚀 [NODOS BDH] Iniciando orquestador Flask...")
    # Ejecuta el servidor Flask en un subproceso independiente
    servidor = subprocess.Popen(["python", "app.py"])
    
    # Espera a que el puerto se estabilice
    time.sleep(2)
    
    print("👁 [SISTEMA] Desplegando interfaz en localhost:5000...")
    webbrowser.open("http://localhost:5000")

if __name__ == "__main__":
    desplegar_sistema()