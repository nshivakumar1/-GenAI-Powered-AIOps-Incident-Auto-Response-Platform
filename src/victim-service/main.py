import time
import psutil
import threading
import logging
from fastapi import FastAPI, APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from jira import JIRA
import requests
from requests.auth import HTTPBasicAuth
import os

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("victim-service")

app = FastAPI(title="Victim Service", version="1.0")
router = APIRouter(prefix="/api")

# Jira Client for Frontend
JIRA_SERVER = os.environ.get("JIRA_SERVER", "https://nakulshivakumar.atlassian.net")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "nakul.shivakumar@gmail.com")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN")

def get_jira_client():
    if not JIRA_API_TOKEN:
        logger.warning("JIRA_API_TOKEN not set")
        return None
    
    options = {"server": JIRA_SERVER, "rest_api_version": "3", "agile_rest_path": "agile"}
    return JIRA(options=options, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

# Global flags for simulation
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

@router.get("/")
def read_root():
    return {"status": "healthy", "service": "victim-service"}

@router.get("/health")
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



# ... (Previous imports are handled by replacing the top block or just adding these if I can.
# To be safe, I will include imports in the top block modification or ensure I don't break typical structure.
# But replacing separate chunks is safer.

@router.get("/incidents")
def get_incidents():
    # Direct requests implementation to bypass library issues
    if not JIRA_API_TOKEN:
         return []

    url = f"{JIRA_SERVER}/rest/api/3/search/jql"
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    query = {
        "jql": "project=AIO ORDER BY created DESC",
        "maxResults": 10,
        "fields": ["summary", "status", "priority", "created"]
    }

    try:
        logger.info(f"Fetching incidents from: {url}")
        response = requests.post(url, json=query, headers=headers, auth=auth)
        logger.info(f"Jira Response Status: {response.status_code}")
        logger.info(f"Jira Response Body: {response.text}") # LOG EVERYTHING
        
        response.raise_for_status()
        data = response.json()
        
        incidents = []
        for issue in data.get('issues', []):
            fields = issue.get('fields', {})
            incidents.append({
                "key": issue.get('key'),
                "summary": fields.get('summary'),
                "status": fields.get('status', {}).get('name'),
                "priority": fields.get('priority', {}).get('name'),
                "created": fields.get('created'),
                "time": fields.get('created')
            })
        logger.info(f"Parsed {len(incidents)} incidents.")
        return incidents
    except Exception as e:
        logger.error(f"Failed to fetch Jira issues (Manual): {e}")
        if 'response' in locals():
             logger.error(f"Response: {response.text}")
        return []


@router.post("/simulate/cpu-spike")
def trigger_cpu_spike(background_tasks: BackgroundTasks, duration: int = 60):
    global cpu_stress_active
    if cpu_stress_active:
        return {"message": "CPU spike already active"}
    
    cpu_stress_active = True
    background_tasks.add_task(burn_cpu)
    
    # Auto-stop after duration
    def stop_cpu():
        global cpu_stress_active
        time.sleep(duration)
        cpu_stress_active = False
        logger.info("CPU spike auto-stopped")

    threading.Thread(target=stop_cpu).start()
    return {"message": f"CPU spike triggered for {duration} seconds"}

@router.post("/simulate/memory-leak")
def trigger_memory_leak(background_tasks: BackgroundTasks):
    global memory_leak_active, memory_store
    memory_leak_active = True
    logger.warning("Memory Leak STARTED")
    
    def generate_leak():
        try:
            for _ in range(100):
                memory_store.append(" " * 10 * 1024 * 1024)
                time.sleep(0.1)
        except MemoryError:
            logger.critical("Memory Error: OOM")

    background_tasks.add_task(generate_leak)
    return {"message": "Memory leak simulated (approx 1GB added)"}

@router.post("/simulate/crash")
def trigger_crash():
    logger.critical("CRITICAL FAILURE: Service crashing forcefully")
    import os
    os._exit(1)

@router.post("/reset")
def reset_simulation():
    global cpu_stress_active, memory_store
    cpu_stress_active = False
    memory_store = []
    logger.info("Simulations reset. System returning to normal.")
    return {"message": "All simulations stopped and memory cleared"}

app.include_router(router)
