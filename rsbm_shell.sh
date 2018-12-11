#!/bin/bash

rsbm_path="$(pwd)/rsbm.py"
clear

input=""
echo "Welcome to Rose's Simple Budget Manager (RSBM)"
echo
$rsbm_path list budgets

while true; do
	echo -n "rsbm> "
	read input
	clear

	if [ "$input" = "exit" ]; then
		exit;
	else
		echo "rsbm> $input"
		$rsbm_path $input
	fi
done
