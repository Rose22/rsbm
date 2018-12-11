# This module handles the saving and loading of data for use by the program

import os
import yaml
import json

from config import *

class StorageManager():
    """Handles saving and loading of data"""

    def __init__(self):
        self.data = []
        init_data = {
            'income': [],
            'budgets': [],
            'budget_leftovers': {},
            'expenses': [],
            'monthly_bills': [],
        }

        if not os.path.exists(CONFIG['path']):
            os.mkdir(CONFIG['path'])

        # Create our save file
        if not os.path.exists(CONFIG['path']+'current_month.json'):
            save_file = open(CONFIG['path']+'current_month.json', 'w')
            save_file.write(json.dumps(init_data))
            save_file.close()

        with open(CONFIG['path']+'current_month.json', 'rb') as f:
            self.data = json.loads(f.read())

    def save(self):
        with open(CONFIG['path']+'current_month.json', 'w') as f:
            return f.write(json.dumps(self.data, indent=4))
