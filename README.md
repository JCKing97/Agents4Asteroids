# Agents for Asteroids

Welcome to the Agents for Asteroids brought to you by AutonomyLab.

Artificial intelligence techniques have been applied to game playing scenarios for a long time.

Asteroids is a classic game in which a player avoids asteroids in space while being able to break the asteroids down with their particle canon.

The purpose of this repository is to house development documents and source code for a project focused on developing an Asteroids like game and building agents to play this game using AI techniques such as reinforcement learning.

It has also been considered that this may be extended into a multi-player game in which agents playing the game can work together and communicate to protect themselves against the asteroids. In this scenario the game may be changed to include a bigger map and limit the observation area of each spacecraft.

# To install and run the game

Ensure you have python installed (this has only been tested on python 3.7 on ubuntu).

- Clone the repository `git clone https://github.com/autonomy-lab/Agents4Asteroids.git`.
- Create a virtual environment `python3.7 -m pip install virtualenv` and `python3.7 -m venv myvenv`
- Activate the virtual environment `source myvenv/bin/activate`
- Install requirements `python -m pip install -r requirements.txt`
- Run the game `python main.py`
- A window with the asteroids menu screen should appear