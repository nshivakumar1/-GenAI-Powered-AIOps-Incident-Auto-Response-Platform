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
    """
    Create and return a configured JIRA client authenticated with environment credentials.
    
    If the environment variable `JIRA_API_TOKEN` is not set, logs a warning and returns `None`.
    
    Returns:
        JIRA or None: An authenticated `JIRA` client configured with server, REST API version 3, and agile path, or `None` if no API token is available.
    """
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
    """
    Continuously performs CPU-intensive work until the global flag `cpu_stress_active` is cleared.
    
    This function runs a tight, CPU-heavy loop to increase processor utilization and stops only when the module-level boolean `cpu_stress_active` becomes False. It is intended for short-lived stress testing and does not return a value.
    """
    global cpu_stress_active
    logger.warning("CPU Stress Test STARTED")
    while cpu_stress_active:
        [x**2 for x in range(10000)]
    logger.info("CPU Stress Test STOPPED")

@router.get("/")
def read_root():
    """
    Provide a simple health payload for the root endpoint.
    
    Returns:
        health_payload (dict): Dictionary with keys 'status' (value 'healthy') and 'service' (value 'victim-service').
    """
    return {"status": "healthy", "service": "victim-service"}

@router.get("/health")
def health_check():
    """
    Check system CPU and memory usage and report service health.
    
    If CPU usage is greater than 80%, returns a 503 JSONResponse with reason "high_cpu". If memory usage is greater than 80%, returns a 503 JSONResponse with reason "high_memory". Otherwise returns a dictionary with "status" set to "healthy" and the current "cpu" and "memory" percentages.
    
    Returns:
        JSONResponse or dict: A 503 JSONResponse with {"status": "unhealthy", "reason": "<high_cpu|high_memory>"} on overload, or {"status": "healthy", "cpu": <cpu_percent>, "memory": <memory_percent>} when healthy.
    """
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
    """
    Fetches recent incidents from the Jira project "AIO" via the Jira REST API and returns them as a list of incident dictionaries.
    
    Returns:
        list: A list of incident dictionaries with keys:
            - `key`: issue key (str)
            - `summary`: issue summary (str or None)
            - `status`: status name (str or None)
            - `priority`: priority name (str or None)
            - `created`: creation timestamp (str or None)
            - `time`: same value as `created` (str or None)
        Returns an empty list if the Jira API token is not set or if any error occurs while fetching or parsing issues.
    """
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
    """
    Trigger a CPU stress simulation for a limited duration.
    
    Starts a background CPU-intensive routine and schedules an automatic stop after the specified duration; if a CPU spike is already active, no new spike is started.
    
    Parameters:
        duration (int): Duration in seconds for which the CPU spike should run.
    
    Returns:
        dict: A message indicating whether the CPU spike was triggered (contains the duration) or that a spike is already active.
    """
    global cpu_stress_active
    if cpu_stress_active:
        return {"message": "CPU spike already active"}
    
    cpu_stress_active = True
    background_tasks.add_task(burn_cpu)
    
    # Auto-stop after duration
    def stop_cpu():
        """
        Waits for the configured duration and disables the CPU stress routine by setting the global `cpu_stress_active` flag to False.
        
        This function blocks for the duration value available in the surrounding scope and then clears `cpu_stress_active`, causing any running CPU stress loop to stop.
        """
        global cpu_stress_active
        time.sleep(duration)
        cpu_stress_active = False
        logger.info("CPU spike auto-stopped")

    threading.Thread(target=stop_cpu).start()
    return {"message": f"CPU spike triggered for {duration} seconds"}

@router.post("/simulate/memory-leak")
def trigger_memory_leak(background_tasks: BackgroundTasks):
    """
    Start a background task that progressively allocates memory to simulate a memory leak.
    
    Schedules a background worker that appends large strings to the module-level memory_store (causing memory usage to grow) and sets the module flag memory_leak_active to True. If allocation fails, a critical OOM log is emitted.
    
    Parameters:
        background_tasks (BackgroundTasks): FastAPI BackgroundTasks used to schedule the leak generator.
    
    Returns:
        dict: A message confirming the memory leak simulation and an approximate amount of memory added.
    """
    global memory_leak_active, memory_store
    memory_leak_active = True
    logger.warning("Memory Leak STARTED")
    
    def generate_leak():
        """
        Simulates a memory leak by appending large strings to the global memory_store in repeated iterations.
        
        Performs up to 100 allocations of approximately 10 MiB each, sleeping briefly between iterations to drive gradual memory growth. If allocation fails due to out-of-memory, logs a critical "Memory Error: OOM" message.
        """
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
    """
    Forcefully terminate the running process with exit code 1.
    
    This ends the Python process immediately (no cleanup handlers or exception propagation).
    """
    logger.critical("CRITICAL FAILURE: Service crashing forcefully")
    import os
    os._exit(1)

@router.post("/reset")
def reset_simulation():
    """
    Stop any active simulation (CPU or memory) and clear the in-memory leak store.
    
    Returns:
        dict: A dictionary with a 'message' confirming that simulations were stopped and memory was cleared.
    """
    global cpu_stress_active, memory_store
    cpu_stress_active = False
    memory_store = []
    logger.info("Simulations reset. System returning to normal.")
    return {"message": "All simulations stopped and memory cleared"}

app.include_router(router)