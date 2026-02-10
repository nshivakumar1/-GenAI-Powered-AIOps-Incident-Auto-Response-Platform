import time
import psutil
import threading
import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("victim-service")

app = FastAPI(title="Victim Service", version="1.0")

# Global flags for simulation
cpu_stress_active = False
memory_leak_active = False
memory_store = []

def burn_cpu():
    global cpu_stress_active
    logger.warning("CPU Stress Test STARTED")
    while cpu_stress_active:
        [x**2 for x in range(10000)]
    logger.info("CPU Stress Test STOPPED")

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "victim-service"}

@app.get("/health")
def health_check():
    cpu_usage = psutil.cpu_percent()
    mem_usage = psutil.virtual_memory().percent
    
    if cpu_usage > 80:
        logger.error(f"High CPU Usage Detected: {cpu_usage}%")
        return JSONResponse(status_code=503, content={"status": "unhealthy", "reason": "high_cpu"})
    
    if mem_usage > 80:
        logger.error(f"High Memory Usage Detected: {mem_usage}%")
        return JSONResponse(status_code=503, content={"status": "unhealthy", "reason": "high_memory"})

    return {"status": "healthy", "cpu": cpu_usage, "memory": mem_usage}

@app.post("/simulate/cpu-spike")
def trigger_cpu_spike(duration: int = 60):
    global cpu_stress_active
    if cpu_stress_active:
        return {"message": "CPU spike already active"}
    
    cpu_stress_active = True
    threading.Thread(target=burn_cpu).start()
    
    # Auto-stop after duration
    def stop_cpu():
        global cpu_stress_active
        time.sleep(duration)
        cpu_stress_active = False
        logger.info("CPU spike auto-stopped")

    threading.Thread(target=stop_cpu).start()
    return {"message": f"CPU spike triggered for {duration} seconds"}

@app.post("/simulate/memory-leak")
def trigger_memory_leak():
    global memory_leak_active, memory_store
    memory_leak_active = True
    logger.warning("Memory Leak STARTED")
    
    # Append 10MB strings repeatedly
    try:
        for _ in range(100):
            memory_store.append(" " * 10 * 1024 * 1024)
            time.sleep(0.1)
    except MemoryError:
        logger.critical("Memory Error: OOM")
    
    return {"message": "Memory leak simulated (approx 1GB added)"}

@app.post("/simulate/crash")
def trigger_crash():
    logger.critical("CRITICAL FAILURE: Service crashing forcefully")
    import os
    os._exit(1)

@app.post("/reset")
def reset_simulation():
    global cpu_stress_active, memory_store
    cpu_stress_active = False
    memory_store = []
    logger.info("Simulations reset. System returning to normal.")
    return {"message": "All simulations stopped and memory cleared"}
