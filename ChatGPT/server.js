const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

const Chess = require('chess.js').Chess; // You will need to install the chess.js library

let game = new Chess();

io.on('connection', (socket) => {
  console.log('a user connected');

  socket.on('disconnect', () => {
    console.log('user disconnected');
  });

  socket.on('move', (move) => {
    // Make the move on the server-side game
    game.move(move);

    // Check if the game is over
    if (game.game_over()) {
      io.emit('game over', game.in_checkmate() ? 'checkmate' : 'stalemate');
    } else {
      // Calculate the computer's move
      let computerMove = minimaxRoot(2, game, true);
      game.move(computerMove);
      io.emit('move', computerMove);

      if (game.game_over()) {
        io.emit('game over', game.in_checkmate() ? 'checkmate' : 'stalemate');
      }
    }
  });
});

server.listen(3000, () => {
  console.log('listening on *:3000');
});

function minimaxRoot(depth, game, isMaximizing) {
  let newGameMoves = game.ugly_moves();
  let bestMove = -9999;
  let bestMoveFound;

  for (let i = 0; i < newGameMoves.length; i++) {
    let newGameMove = newGameMoves[i];
    game.ugly_move(newGameMove);
    let value = minimax(depth - 1, game, -10000, 10000, !isMaximizing);
    game.undo();
    if (value >= bestMove) {
      bestMove = value;
      bestMoveFound = newGameMove;
    }
  }

  return bestMoveFound;
}

function minimax(depth, game, alpha, beta, isMaximizing) {
  if (depth === 0) {
    return -evaluateBoard(game.board());
  }

  let newGameMoves = game.ugly_moves();

  if (isMaximizing) {
    let bestMove = -9999;
    for (let i = 0; i < newGameMoves.length; i++) {
      game.ugly_move(newGameMoves[i]);
      bestMove = Math.max(bestMove, minimax(depth - 1, game, alpha, beta, !isMaximizing));
      game.undo();
      alpha = Math.max(alpha, bestMove);
      if (beta <= alpha) {
        return bestMove
      }
    }
  }
}
