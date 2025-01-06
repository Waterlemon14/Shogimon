Welcome to Shogimon!
===

This project is brought to you by **Eisenhower Aldemita**, **Abram Josh Marcelo**, **Christopher Senatin**, and **Jose Ernesto Tomanan**.
This shall serve as the game manual.

The bottom player, consisting of non-shiny pieces, serves as Player 1 (and is the first to move), while the top player, consisting of shiny pieces, serves as Player 2.
Your player number is displayed on the left side of the screen when launching the online version of the client.

For each round, each player has 3 actions which can either be used by *moving a piece* (i.e., clicking on the on-board piece and clicking a blue dot, which indicates that they can move there); or by *dropping a captured piece* (i.e., clicking on one of your captures and placing them on one of the blue dots shown on screen).
Your on-screen player number will turn green when it is your turn, and white when it is the opponent's turn.

The game is won by trapping the enemy *Latias* and *Latios* in such a way that it cannot move any further.
Similarly, the game is lost by having your own *Latias* and *Latios* trapped.

To start the online (i.e. main) version of the game, run in terminal:

```
poetry run python src/main.py
```

Similarly, the offline, pass-and-play version is also accessible via:

```
poetry run python src/main_offline.py
```

The game can be restarted at any point the program is running by clicking `R`.

Disclaimer
---

Please note that this game's graphics are not owned by the creators, and are purely used for demonstration purposes only.