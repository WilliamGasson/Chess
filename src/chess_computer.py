"""
chess_computer.py

chess bot to play against
based off https://www.youtube.com/watch?v=-QHAPDk5tgs&ab_channel=EddieSharick
"""

__date__ = "2022-12-30"
__author__ = "WilliamGasson"
__version__ = "0.1"


# %% --------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------
import random

# %% --------------------------------------------------------------------------
# Random move computer
# -----------------------------------------------------------------------------

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]


# %% --------------------------------------------------------------------------
#  Best move computer
# -----------------------------------------------------------------------------

def findBestMove(validMoves):
    
    pass
