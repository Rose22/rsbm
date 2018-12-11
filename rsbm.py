#!/usr/bin/python

# RSBM - "Rose's Simple Budget Manager"

import os
import sys

# Import all the stuff specific to RSBM
from config import *
import rsbm_storage
import rsbm_main_interpreter

# Save file system
app_storage = rsbm_storage.StorageManager()

app_functions = {
}

# Heart of the program
app_interpreter = rsbm_main_interpreter.MainInterpreter(app_storage)
cmd_output = app_interpreter.interpret(sys.argv)

if cmd_output not in [True, None]:
    print cmd_output
