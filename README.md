[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/SsQ6IvG7)

Welcome to Shogimon!
===

This project is brought to you by **Eisenhower Aldemita**, **Abram Josh Marcelo**, **Christopher Senatin**, and **Jose Ernesto Tomanan**.
This shall serve as the game manual.

The bottom player, consisting of non-shiny pieces, serves as Player 1 (and is the first to move), while the top player, consisting of shiny pieces, serves as Player 2.

For each round, each player has 3 actions which can either be used by *moving a piece* (i.e., clicking on the on-board piece and clicking a blue dot, which indicates that they can move there); or by *dropping a captured piece* (i.e., clicking on one of your captures and placing them on one of the blue dots shown on screen).

The game is won by trapping the enemy *Latias* and *Latios* in such a way that it cannot move any further.
Similarly, the game is lost by having your own *Latias* and *Latios* trapped.

Python implementation
---

For the Python client, to start the online (i.e. main) version of the game, run in terminal:

```
poetry run python src/main.py
```

Similarly, the offline, pass-and-play version is also accessible via:

```
poetry run python src/main_offline.py
```

Upon launching, you will see your assigned player number displayed on the left side of the screen when launching the online version of the client.
Your on-screen player number will turn green when it is your turn, and white when it is the opponent's turn.

The offline version of the game can be restarted at any point of the program by clicking `R`. For the online implementation, a clean restart is needed (i.e., both the clients and the server).

Disclaimer
---

Please note that this game's graphics are not owned by the creators, and are purely used for demonstration purposes only.