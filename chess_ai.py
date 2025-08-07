import random
import time
import copy
import multiprocessing
from typing import Dict, List, Tuple, Optional, Any

# Simple transposition table implementation
class SimpleTranspositionTable:
    def __init__(self, size_mb: int = 64):
        self.size = (size_mb * 1024 * 1024) // 24  # Estimate entry size
        self.table: Dict[int, Tuple[int, int, str, Any]] = {}
        self.hits = 0
        self.stores = 0

    def lookup(self, key: int, depth: int) -> Optional[Tuple[int, str, Any]]:
        if key in self.table:
            stored_score, stored_depth, stored_flag, stored_move = self.table[key]
            if stored_depth >= depth:
                self.hits += 1
                return stored_score, stored_flag, stored_move
        return None

    def store(self, key: int, score: int, depth: int, flag: str, best_move: Any = None):
        if len(self.table) >= self.size:
            # Simple replacement: remove random entry
            key_to_remove = random.choice(list(self.table.keys()))
            del self.table[key_to_remove]
        
        self.table[key] = (score, depth, flag, best_move)
        self.stores += 1

    def clear(self):
        self.table.clear()
        self.hits = 0
        self.stores = 0

# Simple position hashing
def simple_position_hash(gs) -> int:
    """Create a simple hash of the board position."""
    hash_value = 0
    for row in range(8):
        for col in range(8):
            piece = gs.board[row][col]
            if piece != "--":
                # Simple hash combining piece type, color, and position
                piece_hash = hash(piece) ^ hash((row, col))
                hash_value ^= piece_hash
    
    # Include turn to move
    hash_value ^= hash(gs.white_to_move)
    return hash_value

# Global instances
tt = SimpleTranspositionTable(64)  # 64MB transposition table

piece_score = {'K': 0, 'Q': 9, 'R': 5, 'B': 3, 'N': 3, 'p': 1}

white_knight_scores = [[-50, -40, -30, -30, -30, -30, -40, -50],
 [-40, -20,   0,   0,   0,   0, -20, -40],
 [-30,   0,  10,  15,  15,  10,   0, -30],
 [-30,   5,  15,  20,  20,  15,   5, -30],
 [-30,   0,  15,  20,  20,  15,   0, -30],
 [-30,   5,  10,  15,  15,  10,   5, -30],
 [-40, -20,   0,   5,   5,   0, -20, -40],
 [-50, -40, -30, -30, -30, -30, -40, -50]]

black_knight_scores = [[-50, -40, -30, -30, -30, -30, -40, -50],
 [-40, -20,   0,   5,   5,   0, -20, -40],
 [-30,   5,  10,  15,  15,  10,   5, -30],
 [-30,   0,  15,  20,  20,  15,   0, -30],
 [-30,   5,  15,  20,  20,  15,   5, -30],
 [-30,   0,  10,  15,  15,  10,   0, -30],
 [-40, -20,   0,   0,   0,   0, -20, -40],
 [-50, -40, -30, -30, -30, -30, -40, -50]]

white_bishop_scores = [[-20, -10, -10, -10, -10, -10, -10, -20],
 [-10,   0,   0,   0,   0,   0,   0, -10],
 [-10,   0,   5,  10,  10,   5,   0, -10],
 [-10,   5,   5,  10,  10,   5,   5, -10],
 [-10,   0,  10,  10,  10,  10,   0, -10],
 [-10,  10,  10,  10,  10,  10,  10, -10],
 [-10,   5,   0,   0,   0,   0,   5, -10],
 [-20, -10, -10, -10, -10, -10, -10, -20]]

black_bishop_scores = [[-20, -10, -10, -10, -10, -10, -10, -20],
 [-10,   5,   0,   0,   0,   0,   5, -10],
 [-10,  10,  10,  10,  10,  10,  10, -10],
 [-10,   0,  10,  10,  10,  10,   0, -10],
 [-10,   5,   5,  10,  10,   5,   5, -10],
 [-10,   0,   5,  10,  10,   5,   0, -10],
 [-10,   0,   0,   0,   0,   0,   0, -10],
 [-20, -10, -10, -10, -10, -10, -10, -20]]

white_queen_scores = [[-20, -10, -10,  -5,  -5, -10, -10, -20],
				[-10,   0,   0,   0,   0,   0,   0, -10],
				[-10,   0,   5,   5,   5,   5,   0, -10],
				[ -5,   0,   5,   5,   5,   5,   0,  -5],
				[  0,   0,   5,   5,   5,   5,   0,  -5],
				[-10,   5,   5,   5,   5,   5,   0, -10],
				[-10,   0,   5,   0,   0,   0,   0, -10],
				[-20, -10, -10,  -5,  -5, -10, -10, -20]]

black_queen_scores = [[-20, -10, -10,  -5,  -5, -10, -10, -20],
					 [-10,   0,   5,   0,   0,   0,   0, -10],
					 [-10,   5,   5,   5,   5,   5,   0, -10],
					 [  0,   0,   5,   5,   5,   5,   0,  -5],
					 [ -5,   0,   5,   5,   5,   5,   0,  -5],
					 [-10,   0,   5,   5,   5,   5,   0, -10],
					 [-10,   0,   0,   0,   0,   0,   0, -10],
					 [-20, -10, -10,  -5,  -5, -10, -10, -20]]

black_rook_scores = [[ 0,  0,  0,  5,  5,  0,  0,  0],
					 [-5,  0,  0,  0,  0,  0,  0, -5],
					 [-5,  0,  0,  0,  0,  0,  0, -5],
					 [-5,  0,  0,  0,  0,  0,  0, -5],
					 [-5,  0,  0,  0,  0,  0,  0, -5],
					 [-5,  0,  0,  0,  0,  0,  0, -5],
					 [ 5, 10, 10, 10, 10, 10, 10,  5],
					 [ 0,  0,  0,  0,  0,  0,  0,  0]]

white_rook_scores = [[ 0,  0,  0,  0,  0,  0,  0,  0],
					 [ 5, 10, 10, 10, 10, 10, 10,  5],
					 [-5,  0,  0,  0,  0,  0,  0, -5],
					 [-5,  0,  0,  0,  0,  0,  0, -5],
					 [-5,  0,  0,  0,  0,  0,  0, -5],
					 [-5,  0,  0,  0,  0,  0,  0, -5],
					 [-5,  0,  0,  0,  0,  0,  0, -5],
					 [ 0,  0,  0,  5,  5,  0,  0,  0]]

white_pawn_scores = [[  0,   0,   0,   0,   0,   0,   0,   0],
					 [ 50,  50,  50,  50,  50,  50,  50,  50],
					 [ 10,  10,  20,  30,  30,  20,  10,  10],
					 [  5,   5,  10,  25,  25,  10,   5,   5],
					 [  0,   0,   0,  20,  20,   0,   0,   0],
					 [  5,  -5, -10,   0,   0, -10,  -5,   5],
					 [  5,  10,  10, -20, -20,  10,  10,   5],
					 [  0,   0,   0,   0,   0,   0,   0,   0]]

black_pawn_scores = [[  0,   0,   0,   0,   0,   0,   0,   0],
					 [  5,  10,  10, -20, -20,  10,  10,   5],
					 [  5,  -5, -10,   0,   0, -10,  -5,   5],
					 [  0,   0,   0,  20,  20,   0,   0,   0],
					 [  5,   5,  10,  25,  25,  10,   5,   5],
					 [ 10,  10,  20,  30,  30,  20,  10,  10],
					 [ 50,  50,  50,  50,  50,  50,  50,  50],
					 [  0,   0,   0,   0,   0,   0,   0,   0]]

piece_position_scores = {
    "w": {"p": white_pawn_scores, "N": white_knight_scores, "B": white_bishop_scores, 
          "R": white_rook_scores, "Q": white_queen_scores}, 
    "b": {"p": black_pawn_scores, "N": black_knight_scores, "B": black_bishop_scores, 
          "R": black_rook_scores, "Q": black_queen_scores}
}

# Global variables
next_move = None
counter = 0
find_book_move = False  # Disabled for now

CHECKMATE = 100000
STALEMATE = 0
DEPTH = 4

class ChessAI:
    """Chess AI Engine with optimizations for higher depth search."""
    
    def __init__(self, depth: int = 4, time_limit: float = 30.0):
        self.depth = depth
        self.time_limit = time_limit
        self.nodes_searched = 0
        self.start_time = 0
        
    def get_best_move(self, gs, use_iterative_deepening: bool = True) -> Any:
        """Get the best move for the current position."""
        global tt, counter, next_move
        
        valid_moves = gs.get_valid_moves()
        if not valid_moves:
            return None
            
        # Clear global state
        counter = 0
        next_move = None
        self.nodes_searched = 0
        
        if len(valid_moves) == 1:
            print("Only one legal move available")
            return valid_moves[0]
        
        if use_iterative_deepening:
            return self._iterative_deepening_search(gs, valid_moves)
        else:
            return self._fixed_depth_search(gs, valid_moves)
    
    def _iterative_deepening_search(self, gs, valid_moves) -> Any:
        """Perform iterative deepening with time management."""
        global next_move
        
        self.start_time = time.time()
        best_move = None
        
        for current_depth in range(1, self.depth + 1):
            print(f"Searching depth {current_depth}...")
            
            # Check time limit
            if time.time() - self.start_time > self.time_limit * 0.8:
                print(f"Time limit approaching, stopping at depth {current_depth - 1}")
                break
                
            # Search at current depth
            self._search_root(gs, valid_moves, current_depth)
            
            if next_move:
                best_move = next_move
                elapsed = time.time() - self.start_time
                print(f"Depth {current_depth} completed in {elapsed:.2f}s, nodes: {counter}")
                
            # If we found a checkmate, no need to search deeper
            if abs(counter) > CHECKMATE - 1000:
                print("Checkmate found, stopping search")
                break
                
        return best_move
    
    def _fixed_depth_search(self, gs, valid_moves) -> Any:
        """Perform fixed depth search."""
        self.start_time = time.time()
        self._search_root(gs, valid_moves, self.depth)
        return next_move
    
    def _search_root(self, gs, valid_moves, depth):
        """Root search function."""
        global next_move, counter
        
        # Order moves for better pruning
        ordered_moves = self._order_moves_advanced(gs, valid_moves)
        
        alpha = -CHECKMATE
        beta = CHECKMATE
        turn_multiplier = 1 if gs.white_to_move else -1
        
        best_score = -CHECKMATE
        best_move = None
        
        for i, move in enumerate(ordered_moves):
            # Check time limit periodically
            if i % 10 == 0 and time.time() - self.start_time > self.time_limit:
                print("Time limit reached during search")
                break
                
            gs.make_move(move)
            
            # Use full window for first move, then narrow window for others
            if i == 0:
                score = -self._search(gs, depth - 1, -beta, -alpha, -turn_multiplier)
            else:
                # Try null window search first
                score = -self._search(gs, depth - 1, -alpha - 1, -alpha, -turn_multiplier)
                if alpha < score < beta:
                    # Full re-search if null window failed
                    score = -self._search(gs, depth - 1, -beta, -alpha, -turn_multiplier)
            
            gs.undo_move()
            
            print(f"Move {move}: {score}")
            
            if score > best_score:
                best_score = score
                best_move = move
                next_move = move
                
                if score > alpha:
                    alpha = score
    
    def _search(self, gs, depth: int, alpha: int, beta: int, turn_multiplier: int) -> int:
        """Main minimax search with optimizations."""
        global counter
        counter += 1
        self.nodes_searched += 1
        
        # Check time limit
        if self.nodes_searched % 1000 == 0:
            if time.time() - self.start_time > self.time_limit:
                return turn_multiplier * self._evaluate_position(gs)
        
        # Transposition table lookup
        pos_hash = simple_position_hash(gs)
        tt_entry = tt.lookup(pos_hash, depth)
        if tt_entry:
            score, flag, stored_move = tt_entry
            if flag == "EXACT":
                return score
            elif flag == "ALPHA" and score <= alpha:
                return alpha
            elif flag == "BETA" and score >= beta:
                return beta
        
        # Terminal nodes
        if depth == 0:
            return self._quiescence_search(gs, alpha, beta, turn_multiplier)
        
        # Check for checkmate/stalemate
        valid_moves = gs.get_valid_moves()
        if not valid_moves:
            if gs.checkmate:
                return -CHECKMATE + (DEPTH - depth)  # Prefer faster mates
            else:
                return STALEMATE
        
        # Main search
        original_alpha = alpha
        best_move = None
        best_score = -CHECKMATE
        
        # Order moves
        ordered_moves = self._order_moves_advanced(gs, valid_moves, tt_entry[2] if tt_entry else None)
        
        for move in ordered_moves:
            gs.make_move(move)
            score = -self._search(gs, depth - 1, -beta, -alpha, -turn_multiplier)
            gs.undo_move()
            
            if score > best_score:
                best_score = score
                best_move = move
                
            if score > alpha:
                alpha = score
                
            if alpha >= beta:
                break  # Beta cutoff
        
        # Store in transposition table
        if best_score <= original_alpha:
            flag = "ALPHA"
        elif best_score >= beta:
            flag = "BETA"
        else:
            flag = "EXACT"
            
        tt.store(pos_hash, best_score, depth, flag, best_move)
        
        return best_score
    
    def _quiescence_search(self, gs, alpha: int, beta: int, turn_multiplier: int) -> int:
        """Quiescence search to avoid horizon effect."""
        global counter
        counter += 1
        
        stand_pat = turn_multiplier * self._evaluate_position(gs)
        
        if stand_pat >= beta:
            return beta
            
        if alpha < stand_pat:
            alpha = stand_pat
        
        # Only consider captures in quiescence
        all_moves = gs.get_valid_moves()
        captures = [move for move in all_moves if self._is_capture(move)]
        
        # Order captures by MVV-LVA
        captures = self._order_moves_advanced(gs, captures)
        
        for move in captures:
            gs.make_move(move)
            score = -self._quiescence_search(gs, -beta, -alpha, -turn_multiplier)
            gs.undo_move()
            
            if score >= beta:
                return beta
                
            if score > alpha:
                alpha = score
                
        return alpha
    
    def _order_moves_advanced(self, gs, moves: List[Any], hash_move: Any = None) -> List[Any]:
        """Advanced move ordering for better pruning."""
        if not moves:
            return []
        
        move_scores = []
        
        for move in moves:
            score = 0
            
            # Hash move gets highest priority
            if hash_move and move == hash_move:
                score += 10000
                
            # Captures (MVV-LVA)
            if self._is_capture(move):
                victim = self._get_captured_piece_value(move)
                attacker = self._get_moving_piece_value(move)
                score += 1000 + (victim * 10 - attacker)
                
            # Promotions
            if self._is_promotion(move):
                score += 900
                
            # Checks (if we can detect them easily)
            # This would require making/unmaking the move, so skip for now
            
            # Killer moves (would require killer move table)
            # History heuristic (would require history table)
            
            move_scores.append((move, score))
        
        # Sort by score descending
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, score in move_scores]
    
    def _is_capture(self, move) -> bool:
        """Check if move is a capture."""
        return hasattr(move, 'piece_captured') and move.piece_captured != "--"
    
    def _is_promotion(self, move) -> bool:
        """Check if move is a pawn promotion."""
        return hasattr(move, 'is_pawn_promotion') and move.is_pawn_promotion
    
    def _get_captured_piece_value(self, move) -> int:
        """Get value of captured piece."""
        if not self._is_capture(move):
            return 0
        piece_type = move.piece_captured[1] if len(move.piece_captured) > 1 else move.piece_captured
        return piece_score.get(piece_type, 0)
    
    def _get_moving_piece_value(self, move) -> int:
        """Get value of moving piece."""
        piece_type = move.piece_moved[1] if len(move.piece_moved) > 1 else move.piece_moved
        return piece_score.get(piece_type, 0)
    
    def _evaluate_position(self, gs) -> int:
        """Evaluate the current position."""
        if gs.checkmate:
            return -CHECKMATE if gs.white_to_move else CHECKMATE
        elif gs.stalemate:
            return STALEMATE
        
        score = 0
        
        # Material and positional evaluation
        for row in range(8):
            for col in range(8):
                piece = gs.board[row][col]
                if piece != "--":
                    color = piece[0]
                    piece_type = piece[1]
                    
                    if piece_type in piece_score:
                        material_value = piece_score[piece_type]
                        
                        # Positional value
                        positional_value = 0
                        if (piece_type != "K" and color in piece_position_scores 
                            and piece_type in piece_position_scores[color]):
                            positional_value = piece_position_scores[color][piece_type][row][col] * 0.01
                        
                        total_value = material_value + positional_value
                        
                        if color == "w":
                            score += total_value
                        else:
                            score -= total_value
        
        return score

# Legacy function interface for backward compatibility
def find_random_move(valid_moves):
    """Return a random move from the list of valid moves."""
    if not valid_moves:
        return None
    return valid_moves[random.randint(0, len(valid_moves) - 1)]

def find_best_move(gs, valid_moves, return_queue):
    """Legacy interface - use ChessAI class instead."""
    ai = ChessAI(depth=DEPTH)
    best_move = ai.get_best_move(gs)
    return_queue.put(best_move)

# Legacy search functions (simplified)
def search(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    """Legacy search function."""
    ai = ChessAI(depth=depth)
    return ai._search(gs, depth, alpha, beta, turn_multiplier)

def order_moves(moves):
    """Legacy move ordering."""
    if not moves:
        return []
    ai = ChessAI()
    return ai._order_moves_advanced(None, moves)

def score_board(gs):
    """Legacy evaluation function."""
    ai = ChessAI()
    return ai._evaluate_position(gs)