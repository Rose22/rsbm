# This module handles the saving and loading of data for use by the program

import os
import yaml

from config import *

class StorageManager():
    def __init__(self):
        self.data = []
        init_data = {
            'income': [],
            'budgets': [],
            'expenses': [],
            'monthly_bills': [],
        }

        if not os.path.exists(CONFIG['path']):
            os.mkdir(CONFIG['path'])

        # Create our save file
        if not os.path.exists(CONFIG['path']+'current_month.yaml'):
            save_file = open(CONFIG['path']+'current_month.yaml', 'w')
            save_file.write(yaml.dump(init_data))
            save_file.close()

        with open(CONFIG['path']+'current_month.yaml', 'rb') as f:
            self.data = yaml.safe_load(f.read())

    def save(self):
        with open(CONFIG['path']+'current_month.yaml', 'w') as f:
            return f.write(yaml.dump(self.data))

    def debug(self):
        print self.data
