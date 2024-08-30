from datetime import datetime
import uuid

def create_unique_id():
  # Get the current date and time
  current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
  # Generate a unique UUID
  unique_id = str(uuid.uuid4())
  # Combine date, time, and UUID into a single variable
  date_time_uuid = f"{current_datetime}_{unique_id}"
  return date_time_uuid
