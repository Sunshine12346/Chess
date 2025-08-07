#!/usr/bin/env python3
"""
Example usage of the improved Chess AI engine.

This demonstrates how to use the ChessAI class for higher depth searches.
"""

import time
from chess_ai import ChessAI, find_random_move, DEPTH

# Mock game state class for demonstration
class MockGameState:
    """Mock game state for testing - replace with your actual game state class."""
    
    def __init__(self):
        # Initialize a standard chess starting position
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True
        self.checkmate = False
        self.stalemate = False
        self.move_count = 0
    
    def get_valid_moves(self):
        """Return a list of mock moves - replace with actual move generation."""
        # This is just a placeholder - implement your actual move generation
        moves = []
        for i in range(10):  # Generate some mock moves
            move = MockMove(f"move_{i}", self.white_to_move)
            moves.append(move)
        return moves
    
    def make_move(self, move):
        """Make a move on the board."""
        self.white_to_move = not self.white_to_move
        self.move_count += 1
        # Implement actual move making logic here
        
    def undo_move(self):
        """Undo the last move."""
        self.white_to_move = not self.white_to_move  
        self.move_count -= 1
        # Implement actual move undoing logic here

class MockMove:
    """Mock move class - replace with your actual move class."""
    
    def __init__(self, move_notation, is_white_move):
        self.notation = move_notation
        self.piece_moved = "wp" if is_white_move else "bp"  # Mock piece
        self.piece_captured = "--"  # No capture by default
        self.is_pawn_promotion = False
        self.promoted_piece = None
        
    def __str__(self):
        return self.notation
    
    def __repr__(self):
        return f"Move({self.notation})"

def demonstrate_chess_ai():
    """Demonstrate the Chess AI with different configurations."""
    
    print("=== Chess AI Demonstration ===\n")
    
    # Create a mock game state
    game_state = MockGameState()
    
    # Test 1: Quick move for comparison
    print("1. Finding a random move (baseline):")
    valid_moves = game_state.get_valid_moves()
    random_move = find_random_move(valid_moves)
    print(f"Random move: {random_move}\n")
    
    # Test 2: Low depth search
    print("2. Chess AI at depth 3:")
    ai_depth_3 = ChessAI(depth=3, time_limit=5.0)
    start_time = time.time()
    best_move_3 = ai_depth_3.get_best_move(game_state, use_iterative_deepening=False)
    time_3 = time.time() - start_time
    print(f"Best move (depth 3): {best_move_3}")
    print(f"Time taken: {time_3:.3f} seconds")
    print(f"Nodes searched: {ai_depth_3.nodes_searched}\n")
    
    # Test 3: Medium depth search  
    print("3. Chess AI at depth 5:")
    ai_depth_5 = ChessAI(depth=5, time_limit=10.0)
    start_time = time.time()
    best_move_5 = ai_depth_5.get_best_move(game_state, use_iterative_deepening=False)
    time_5 = time.time() - start_time
    print(f"Best move (depth 5): {best_move_5}")
    print(f"Time taken: {time_5:.3f} seconds")
    print(f"Nodes searched: {ai_depth_5.nodes_searched}\n")
    
    # Test 4: Iterative deepening with time limit
    print("4. Chess AI with iterative deepening (10 second limit):")
    ai_iterative = ChessAI(depth=8, time_limit=10.0)
    start_time = time.time()
    best_move_iter = ai_iterative.get_best_move(game_state, use_iterative_deepening=True)
    time_iter = time.time() - start_time
    print(f"Best move (iterative): {best_move_iter}")
    print(f"Time taken: {time_iter:.3f} seconds")
    print(f"Nodes searched: {ai_iterative.nodes_searched}\n")
    
    # Test 5: High depth search (if time permits)
    print("5. Chess AI at depth 7 (if you have time!):")
    ai_depth_7 = ChessAI(depth=7, time_limit=30.0)
    start_time = time.time()
    best_move_7 = ai_depth_7.get_best_move(game_state, use_iterative_deepening=False)
    time_7 = time.time() - start_time
    print(f"Best move (depth 7): {best_move_7}")
    print(f"Time taken: {time_7:.3f} seconds")
    print(f"Nodes searched: {ai_depth_7.nodes_searched}\n")
    
    print("=== Performance Summary ===")
    print(f"Depth 3: {time_3:.3f}s")
    print(f"Depth 5: {time_5:.3f}s") 
    print(f"Iterative (10s limit): {time_iter:.3f}s")
    print(f"Depth 7: {time_7:.3f}s")

def usage_recommendations():
    """Print usage recommendations for different scenarios."""
    
    print("\n=== Usage Recommendations ===\n")
    
    print("For RAPID games (< 5 minutes):")
    print("  ai = ChessAI(depth=4, time_limit=2.0)")
    print("  move = ai.get_best_move(game_state, use_iterative_deepening=True)")
    print()
    
    print("For BLITZ games (3-5 minutes):")
    print("  ai = ChessAI(depth=5, time_limit=5.0)")  
    print("  move = ai.get_best_move(game_state, use_iterative_deepening=True)")
    print()
    
    print("For STANDARD games (15+ minutes):")
    print("  ai = ChessAI(depth=7, time_limit=15.0)")
    print("  move = ai.get_best_move(game_state, use_iterative_deepening=True)")
    print()
    
    print("For ANALYSIS (no time pressure):")
    print("  ai = ChessAI(depth=8, time_limit=60.0)")
    print("  move = ai.get_best_move(game_state, use_iterative_deepening=True)")
    print()
    
    print("Key improvements in the fixed version:")
    print("✓ Proper transposition table with 64MB cache")
    print("✓ Advanced move ordering (MVV-LVA, hash moves)")
    print("✓ Quiescence search to avoid horizon effect")
    print("✓ Iterative deepening with time management")
    print("✓ Null window search optimization")
    print("✓ Better evaluation function")
    print("✓ Fixed function signatures and parameter bugs")
    print("✓ Proper alpha-beta pruning implementation")

if __name__ == "__main__":
    # Run the demonstration
    demonstrate_chess_ai()
    
    # Show usage recommendations
    usage_recommendations()
    
    print("\n=== Integration Notes ===")
    print("To integrate with your existing chess engine:")
    print("1. Replace MockGameState with your actual GameState class")
    print("2. Replace MockMove with your actual Move class")
    print("3. Ensure your move class has these attributes:")
    print("   - piece_moved, piece_captured, is_pawn_promotion, promoted_piece")
    print("4. Ensure your game state has these methods:")
    print("   - get_valid_moves(), make_move(), undo_move()")
    print("5. Ensure your game state has these attributes:")
    print("   - white_to_move, checkmate, stalemate, board")