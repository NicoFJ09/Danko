# CODEBASE STRUCTURE

# Constants.py

# Bot utility functions: Advance, turn degrees: requires read gyro, read sensors.

# Memory handling:  store current position (create function to turn gyro readings /current orientation into it)
# data structure with all previous positions as set in checkpoints
# Create a set checkpoint function that handles multiple cases in which one can happen, when a sensore reading changes beyond the
# defined threshold. Handle dead ends aswell since no measurement changes drastically it just goes below the wall threshold.
# Create backtrack function that makes bot turn around 180 and change reference position to go back to last saved checkpoint


