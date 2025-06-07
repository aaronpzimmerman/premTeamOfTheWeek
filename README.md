# Fantasy Premier League Project

This repository shares code and other resources for analyzing various facets of Fantasy Premier League data. I will continue 
to add resources to both track my progress and to share what I have learned/created. 

Scripts:
1) bestTotalSquad.py
Description: Find the fantasy team of the week for a squad made of the highest season total point scorers. This includes all permutations
of formation and player for each gameweek. Outputs saved to "Top Squad TofW" folders when run.
2) bestPerWeek.py
Description: Find the fantasy team of the week for any premier league season, including all permutations of formation and players.
Outputs saved to "Teams of the Week" folders when run.

Tips:
1) Download the season(s) folder(s) you want to work with, bestPerWeek.py and requirements.txt.
2) Create a .venv and run requirements.txt (pip install -r /path/to/requirements.txt)
3) Make sure you have the subfolder "Teams of the Week" under each season folder because that will be the location of your .csv containing all permutations of formation and player. 

Data provided by https://github.com/vaastav/Fantasy-Premier-League
