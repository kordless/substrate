import time
import hashlib
from datetime import datetime, timedelta

def get_chunk_start(time_obj):
    """Get the start of the 5-minute chunk for a given time."""
    return time_obj.replace(minute=time_obj.minute // 5 * 5, second=0, microsecond=0)

def get_time_hash(time_obj):
    """Generate a hash from the given time object."""
    time_str = time_obj.strftime("%Y-%m-%d %H:%M:%S")
    return hashlib.md5(time_str.encode()).hexdigest()

def get_overlapping_hashes(time_obj):
    """Get three overlapping hashes for the given time."""
    current_chunk = get_chunk_start(time_obj)
    previous_chunk = current_chunk - timedelta(minutes=5)
    next_chunk = current_chunk + timedelta(minutes=5)

    return {
        "previous": get_time_hash(previous_chunk),
        "current": get_time_hash(current_chunk),
        "next": get_time_hash(next_chunk)
    }

def main():
    while True:
        now = datetime.now()
        hashes = get_overlapping_hashes(now)
        
        current_chunk_start = get_chunk_start(now)
        previous_chunk_start = current_chunk_start - timedelta(minutes=5)
        next_chunk_start = current_chunk_start + timedelta(minutes=5)

        print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Chunks:")
        print(f"  Previous ({previous_chunk_start.strftime('%H:%M')} - {current_chunk_start.strftime('%H:%M')}): {hashes['previous'][:8]}...")
        print(f"  Current  ({current_chunk_start.strftime('%H:%M')} - {next_chunk_start.strftime('%H:%M')}): {hashes['current'][:8]}...")
        print(f"  Next     ({next_chunk_start.strftime('%H:%M')} - {(next_chunk_start + timedelta(minutes=5)).strftime('%H:%M')}): {hashes['next'][:8]}...")
        print("-" * 70)
        
        time.sleep(10)  # Update every 10 seconds for demonstration

if __name__ == "__main__":
    main()