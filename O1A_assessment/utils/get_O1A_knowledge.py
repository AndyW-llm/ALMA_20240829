import os
import json

def load_json(json_path):
  if os.path.isfile(json_path):
    with open(json_path, 'r') as file:
      data = json.load(file)
  else:
      raise ValueError('[get_O1A_knowledge.py] Could not load knowledge file at:\n', json_path)
  return data
   
O1A_DFFINITIONS = load_json(os.path.abspath("./knowledges/definitions.json"))
