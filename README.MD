# READ ME

Code to create a chess game

## Current state of code:
1. chess_main handles user inputs, displays board.
2. chess_engine stores state data for the game, calcuates valid moves and move log.

## Improvements to be made

1. Adding a machine learning engine that allows you to play the computer.
2. Alternative version of chess_main for online version - the engine can be the same.
3. Asyncronous ai and ui
4. Post game analysis
5. improve scoring method - position
6. create list of gamestates as opposed to log for caslting and enpassant
7. reuse old gamestates instead of recalculating
## UI Improvements
1. Move log panel
2. UI to select pawn promotion
3. UI start game interface - select who is playing what colour

## Bugs

1. checkmate not displaying
2. bot asks for what pawn promotion would be
3. stalemate has a problem with ai - if game is going to end it double stalemate
4. castling is disapearing sometimes with ai