import os
import time
import sys
import warnings
from datetime import datetime, timezone, timedelta
import scratchattach as scratch3
from dotenv import load_dotenv
from scratchattach.utils.exceptions import (
    RateLimitedError, Response429, FetchError,
    Unauthenticated, Unauthorized, LoginFailure, XTokenError
)

warnings.filterwarnings("ignore", category=scratch3.LoginDataWarning)

load_dotenv()

SESSION_ID = os.environ.get("SCRATCH_SESSION_ID")
USERNAME = os.environ.get("SCRATCH_USERNAME")
PROJECT_ID = int(os.environ.get("SCRATCH_PROJECT_ID", 0))
SESSION_EXPIRY = os.environ.get("SESSION_EXPIRY", "")

if not all([SESSION_ID, USERNAME, PROJECT_ID, SESSION_EXPIRY]):
    raise ValueError(
        "Environment variables are missing. Make sure the .env file exists "
        "and contains SCRATCH_SESSION_ID, SCRATCH_USERNAME, SCRATCH_PROJECT_ID and SESSION_EXPIRY"
    )

INTERVAL = 5
MAX_RETRY_WAIT = 600
MAX_AUTH_FAILS = 3

def log_fatal(message):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open("fatal_error.log", "w") as f:
        f.write(f"[{timestamp}] {message}\n")

def parse_expiry(expiry_str):
    return datetime.strptime(expiry_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

expiry_date = parse_expiry(SESSION_EXPIRY)
print(f"Session expires on: {expiry_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
print(f"Script will auto-stop 1 hour before expiry.")

print(f"Connecting to project {PROJECT_ID} as {USERNAME}...")
session = scratch3.login_by_id(SESSION_ID, username=USERNAME)
project = session.connect_project(PROJECT_ID)

print(f"Monitoring statistics of project '{project.title}'...")
print(f"Interval between checks: {INTERVAL} seconds")
print("Server running. Waiting for stat changes...\n")

retry_count = 0
auth_fail_count = 0
was_in_error = False
total_wait = 0

def handle_retryable_error(message, wait_time):
    global was_in_error, total_wait
    print(message)
    was_in_error = True
    total_wait += wait_time
    time.sleep(wait_time)

while True:
    now = datetime.now(timezone.utc)
    margin = timedelta(hours=1)
    if now >= (expiry_date - margin):
        message = "Session ID expired or will expire within 1 hour. Shutting down."
        print(message)
        log_fatal(message)
        sys.exit(0)
    
    try:
        project.update()
        
        loves = project.loves
        favorites = project.favorites
        views = project.views
        
        new_title = f"❤️{loves} ⭐{favorites} ▶{views} | Live stats title"
        
        if project.title != new_title:
            project.set_title(new_title)
            
        if was_in_error:
            print(f"Recovered after {total_wait}s of downtime.")
            was_in_error = False
            total_wait = 0
        
        retry_count = 0
        auth_fail_count = 0
        
    except (Unauthenticated, LoginFailure, XTokenError) as e:
        message = f"FATAL: Session expired or invalid: {e}"
        print(message)
        log_fatal(message)
        sys.exit(1)
        
    except Unauthorized as e:
        auth_fail_count += 1
        print(f"Unauthorized ({auth_fail_count}/{MAX_AUTH_FAILS}): {e}")
        
        if auth_fail_count >= MAX_AUTH_FAILS:
            message = "FATAL: Too many authentication failures. Stopping script."
            print(message)
            log_fatal(message)
            sys.exit(1)
        
        handle_retryable_error("Waiting 5 minutes before retry...", 300)
        continue
        
    except RateLimitedError:
        retry_count += 1
        wait_time = min(2 ** retry_count, MAX_RETRY_WAIT)
        handle_retryable_error(f"Rate limit (scratchattach). Waiting {wait_time}s...", wait_time)
        continue
        
    except Response429:
        retry_count += 1
        wait_time = min(2 ** retry_count, MAX_RETRY_WAIT)
        handle_retryable_error(f"Error 429 from Scratch API. Waiting {wait_time}s...", wait_time)
        continue
        
    except FetchError:
        retry_count += 1
        wait_time = min(2 ** retry_count, MAX_RETRY_WAIT)
        handle_retryable_error(f"Scratch API error (FetchError). Waiting {wait_time}s...", wait_time)
        continue
        
    except Exception as e:
        handle_retryable_error(f"Error: {e}. Trying again in {INTERVAL} seconds...", INTERVAL)
        retry_count = 0
    
    time.sleep(INTERVAL)
