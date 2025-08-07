import random
import time
import copy
import multiprocessing
from typing import Dict, List, Tuple, Optional, Any

# Advanced transposition table with better replacement scheme
class TurboTranspositionTable:
    def __init__(self, size_mb: int = 128):
        self.size = (size_mb * 1024 * 1024) // 32  # Larger entry size for more data
        self.table: Dict[int, Tuple[int, int, str, Any, int]] = {}  # Added age
        self.hits = 0
        self.stores = 0
        self.age = 0

    def lookup(self, key: int, depth: int) -> Optional[Tuple[int, str, Any]]:
        if key in self.table:
            stored_score, stored_depth, stored_flag, stored_move, stored_age = self.table[key]
            if stored_depth >= depth:
                self.hits += 1
                return stored_score, stored_flag, stored_move
        return None

    def store(self, key: int, score: int, depth: int, flag: str, best_move: Any = None):
        if len(self.table) >= self.size:
            # Always replace scheme: prefer higher depth or newer entries
            if key not in self.table:
                # Find entry to replace (prefer older entries with lower depth)
                worst_key = min(self.table.keys(), 
                              key=lambda k: (self.table[k][1], -self.table[k][4]))  # depth, -age
                del self.table[worst_key]
        
        self.table[key] = (score, depth, flag, best_move, self.age)
        self.stores += 1

    def new_search(self):
        """Call this at the start of each new search to update age"""
        self.age += 1

    def clear(self):
        self.table.clear()
        self.hits = 0
        self.stores = 0
        self.age = 0

# Killer moves table for better move ordering
class KillerMoves:
    def __init__(self, max_depth: int = 20):
        # Store 2 killer moves per depth level
        self.killers = [[None, None] for _ in range(max_depth)]
    
    def add_killer(self, depth: int, move: Any):
        if depth < len(self.killers):
            if move != self.killers[depth][0]:
                self.killers[depth][1] = self.killers[depth][0]
                self.killers[depth][0] = move
    
    def is_killer(self, depth: int, move: Any) -> int:
        if depth < len(self.killers):
            if move == self.killers[depth][0]:
                return 2  # Primary killer
            elif move == self.killers[depth][1]:
                return 1  # Secondary killer
        return 0
    
    def clear(self):
        for level in self.killers:
            level[0] = level[1] = None

# History heuristic for move ordering
class HistoryTable:
    def __init__(self):
        # Simple history: piece_type -> to_square -> score
        self.history = {}
        self.max_history = 10000
    
    def add_history(self, move: Any, depth: int):
        key = self._get_move_key(move)
        if key:
            score = depth * depth  # Deeper cutoffs are more valuable
            self.history[key] = self.history.get(key, 0) + score
            # Prevent overflow
            if self.history[key] > self.max_history:
                self._scale_down()
    
    def get_history_score(self, move: Any) -> int:
        key = self._get_move_key(move)
        return self.history.get(key, 0) if key else 0
    
    def _get_move_key(self, move: Any) -> Optional[str]:
        if hasattr(move, 'piece_moved') and hasattr(move, 'notation'):
            return f"{move.piece_moved}_{move.notation}"
        return None
    
    def _scale_down(self):
        """Scale down all history scores to prevent overflow"""
        for key in self.history:
            self.history[key] //= 2
    
    def clear(self):
        self.history.clear()

# Simple position hashing with incremental updates
def turbo_position_hash(gs) -> int:
    """Faster position hashing."""
    # Use a simple but fast hash
    hash_value = 0
    multiplier = 1
    
    for row in range(8):
        for col in range(8):
            piece = gs.board[row][col]
            if piece != "--":
                # Fast hash: combine ASCII values
                piece_val = ord(piece[0]) * 100 + ord(piece[1])
                hash_value += piece_val * multiplier
                multiplier = (multiplier * 7) % 1000000007
    
    # Include turn and simple position info
    hash_value ^= hash(gs.white_to_move) * 12345
    return hash_value

# Global instances
tt_turbo = TurboTranspositionTable(128)  # 128MB table
killer_moves = KillerMoves(20)
history_table = HistoryTable()

piece_score = {'K': 0, 'Q': 900, 'R': 500, 'B': 330, 'N': 320, 'p': 100}

# Simplified piece-square tables for faster access
piece_square_bonus = {
    'p': 10, 'N': 15, 'B': 15, 'R': 0, 'Q': 5, 'K': 0
}

# Global variables
next_move = None
counter = 0

CHECKMATE = 100000
STALEMATE = 0
DEPTH = 4

class TurboChessAI:
    """Ultra-fast Chess AI optimized for depth 10+ searches."""
    
    def __init__(self, depth: int = 10, time_limit: float = 30.0):
        self.depth = depth
        self.time_limit = time_limit
        self.nodes_searched = 0
        self.start_time = 0
        self.null_move_ok = True
        
        # Search parameters
        self.null_move_reduction = 2
        self.lmr_reduction = 1  # Late move reduction
        self.lmr_threshold = 4  # Start LMR after this many moves
        self.futility_margin = 200  # Futility pruning margin
        
    def get_best_move(self, gs, use_iterative_deepening: bool = True) -> Any:
        """Get the best move with ultra-fast search."""
        global tt_turbo, counter, next_move, killer_moves, history_table
        
        valid_moves = gs.get_valid_moves()
        if not valid_moves:
            return None
            
        # Clear global state
        counter = 0
        next_move = None
        self.nodes_searched = 0
        killer_moves.clear()
        tt_turbo.new_search()
        
        if len(valid_moves) == 1:
            print("Only one legal move available")
            return valid_moves[0]
        
        print(f"Starting search with {len(valid_moves)} moves...")
        
        if use_iterative_deepening:
            return self._iterative_deepening_search(gs, valid_moves)
        else:
            return self._fixed_depth_search(gs, valid_moves)
    
    def _iterative_deepening_search(self, gs, valid_moves) -> Any:
        """Iterative deepening with aspiration windows."""
        global next_move
        
        self.start_time = time.time()
        best_move = None
        last_score = 0
        
        for current_depth in range(1, self.depth + 1):
            search_start = time.time()
            
            # Check time limit
            if time.time() - self.start_time > self.time_limit * 0.85:
                print(f"Time limit approaching, stopping at depth {current_depth - 1}")
                break
            
            # Use aspiration windows for depth 3+
            if current_depth >= 3:
                alpha = last_score - 50
                beta = last_score + 50
                
                # Try narrow window first
                score = self._search_root(gs, valid_moves, current_depth, alpha, beta)
                
                # If it failed, research with full window
                if score <= alpha or score >= beta:
                    print(f"Aspiration window failed, researching depth {current_depth}")
                    score = self._search_root(gs, valid_moves, current_depth, -CHECKMATE, CHECKMATE)
            else:
                score = self._search_root(gs, valid_moves, current_depth, -CHECKMATE, CHECKMATE)
            
            if next_move:
                best_move = next_move
                last_score = score
                elapsed = time.time() - search_start
                nps = counter / elapsed if elapsed > 0 else 0
                print(f"Depth {current_depth}: {best_move} ({score}) in {elapsed:.2f}s, {nps:.0f} nps")
                
            # Early termination for checkmate
            if abs(score) > CHECKMATE - 1000:
                print(f"Checkmate found at depth {current_depth}, stopping search")
                break
                
        return best_move
    
    def _fixed_depth_search(self, gs, valid_moves) -> Any:
        """Fixed depth search."""
        self.start_time = time.time()
        self._search_root(gs, valid_moves, self.depth, -CHECKMATE, CHECKMATE)
        return next_move
    
    def _search_root(self, gs, valid_moves, depth, alpha, beta):
        """Root search with advanced move ordering."""
        global next_move, counter
        
        # Get hash move if available
        pos_hash = turbo_position_hash(gs)
        tt_entry = tt_turbo.lookup(pos_hash, depth)
        hash_move = tt_entry[2] if tt_entry else None
        
        # Order moves
        ordered_moves = self._order_moves_turbo(gs, valid_moves, depth, hash_move)
        
        turn_multiplier = 1 if gs.white_to_move else -1
        best_score = -CHECKMATE
        best_move = None
        
        for i, move in enumerate(ordered_moves):
            # Check time limit periodically
            if i % 100 == 0 and time.time() - self.start_time > self.time_limit:
                print("Time limit reached during root search")
                break
                
            gs.make_move(move)
            
            # Principal Variation Search
            if i == 0:
                # Full window search for first move
                score = -self._search_turbo(gs, depth - 1, -beta, -alpha, -turn_multiplier, True)
            else:
                # Null window search
                score = -self._search_turbo(gs, depth - 1, -alpha - 1, -alpha, -turn_multiplier, True)
                if alpha < score < beta:
                    # Re-search with full window
                    score = -self._search_turbo(gs, depth - 1, -beta, -alpha, -turn_multiplier, True)
            
            gs.undo_move()
            
            if score > best_score:
                best_score = score
                best_move = move
                next_move = move
                
                if score > alpha:
                    alpha = score
                    
        return best_score
    
    def _search_turbo(self, gs, depth: int, alpha: int, beta: int, turn_multiplier: int, 
                     allow_null: bool = True) -> int:
        """Ultra-fast search with all optimizations."""
        global counter
        counter += 1
        self.nodes_searched += 1
        
        # Periodic time check
        if self.nodes_searched % 5000 == 0:
            if time.time() - self.start_time > self.time_limit:
                return turn_multiplier * self._evaluate_fast(gs)
        
        # Transposition table lookup
        pos_hash = turbo_position_hash(gs)
        tt_entry = tt_turbo.lookup(pos_hash, depth)
        if tt_entry:
            score, flag, stored_move = tt_entry
            if flag == "EXACT":
                return score
            elif flag == "ALPHA" and score <= alpha:
                return alpha
            elif flag == "BETA" and score >= beta:
                return beta
        
        # Terminal nodes
        if depth <= 0:
            return self._quiescence_search_turbo(gs, alpha, beta, turn_multiplier)
        
        # Check for checkmate/stalemate
        valid_moves = gs.get_valid_moves()
        if not valid_moves:
            if gs.checkmate:
                return -CHECKMATE + (self.depth - depth)  # Prefer faster mates
            else:
                return STALEMATE
        
        # Null move pruning (major speedup!)
        if (allow_null and not gs.checkmate and depth >= 3 and 
            self._has_non_pawn_pieces(gs, gs.white_to_move)):
            
            # Make null move
            gs.white_to_move = not gs.white_to_move
            null_score = -self._search_turbo(gs, depth - 1 - self.null_move_reduction, 
                                           -beta, -beta + 1, -turn_multiplier, False)
            gs.white_to_move = not gs.white_to_move
            
            if null_score >= beta:
                return beta  # Null move cutoff
        
        # Futility pruning for near-leaf nodes
        if depth <= 2 and not gs.checkmate:
            static_eval = turn_multiplier * self._evaluate_fast(gs)
            if static_eval - self.futility_margin >= beta:
                return beta
        
        # Main search
        original_alpha = alpha
        best_move = None
        best_score = -CHECKMATE
        moves_searched = 0
        
        # Get hash move and order moves
        hash_move = tt_entry[2] if tt_entry else None
        ordered_moves = self._order_moves_turbo(gs, valid_moves, depth, hash_move)
        
        for move in ordered_moves:
            gs.make_move(move)
            moves_searched += 1
            
            # Late Move Reductions (LMR)
            reduction = 0
            if (moves_searched > self.lmr_threshold and depth >= 3 and 
                not self._is_capture(move) and not self._is_promotion(move) and not gs.checkmate):
                reduction = self.lmr_reduction
            
            # Search with possible reduction
            if moves_searched == 1:
                # Full search for first move
                score = -self._search_turbo(gs, depth - 1, -beta, -alpha, -turn_multiplier, True)
            else:
                # Try reduced search first
                search_depth = depth - 1 - reduction
                score = -self._search_turbo(gs, search_depth, -alpha - 1, -alpha, -turn_multiplier, True)
                
                # Re-search if needed
                if score > alpha and reduction > 0:
                    score = -self._search_turbo(gs, depth - 1, -alpha - 1, -alpha, -turn_multiplier, True)
                if score > alpha and score < beta:
                    score = -self._search_turbo(gs, depth - 1, -beta, -alpha, -turn_multiplier, True)
            
            gs.undo_move()
            
            if score > best_score:
                best_score = score
                best_move = move
                
            if score > alpha:
                alpha = score
                
            if alpha >= beta:
                # Beta cutoff - add to killer moves and history
                if not self._is_capture(move):
                    killer_moves.add_killer(depth, move)
                    history_table.add_history(move, depth)
                break
        
        # Store in transposition table
        if best_score <= original_alpha:
            flag = "ALPHA"
        elif best_score >= beta:
            flag = "BETA"
        else:
            flag = "EXACT"
            
        tt_turbo.store(pos_hash, best_score, depth, flag, best_move)
        
        return best_score
    
    def _quiescence_search_turbo(self, gs, alpha: int, beta: int, turn_multiplier: int) -> int:
        """Fast quiescence search."""
        global counter
        counter += 1
        
        stand_pat = turn_multiplier * self._evaluate_fast(gs)
        
        if stand_pat >= beta:
            return beta
            
        if alpha < stand_pat:
            alpha = stand_pat
        
        # Only good captures in quiescence
        all_moves = gs.get_valid_moves()
        captures = [move for move in all_moves if self._is_good_capture(move)]
        
        # Order captures by MVV-LVA
        captures.sort(key=self._capture_score, reverse=True)
        
        for move in captures:
            gs.make_move(move)
            score = -self._quiescence_search_turbo(gs, -beta, -alpha, -turn_multiplier)
            gs.undo_move()
            
            if score >= beta:
                return beta
                
            if score > alpha:
                alpha = score
                
        return alpha
    
    def _order_moves_turbo(self, gs, moves: List[Any], depth: int, hash_move: Any = None) -> List[Any]:
        """Ultra-fast move ordering."""
        if not moves:
            return []
        
        move_scores = []
        
        for move in moves:
            score = 0
            
            # Hash move gets highest priority
            if hash_move and self._moves_equal(move, hash_move):
                score += 100000
                
            # Captures (MVV-LVA)
            elif self._is_capture(move):
                victim_value = self._get_captured_piece_value(move)
                attacker_value = self._get_moving_piece_value(move)
                score += 10000 + (victim_value * 10 - attacker_value)
                
            # Promotions
            elif self._is_promotion(move):
                score += 9000
                
            # Killer moves
            else:
                killer_score = killer_moves.is_killer(depth, move)
                if killer_score > 0:
                    score += 8000 + killer_score * 100
                else:
                    # History heuristic
                    score += history_table.get_history_score(move)
            
            move_scores.append((move, score))
        
        # Sort by score descending
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, score in move_scores]
    
    def _is_good_capture(self, move) -> bool:
        """Check if capture is worth searching in quiescence."""
        if not self._is_capture(move):
            return False
        
        # Only captures that gain material or equal trades
        victim_value = self._get_captured_piece_value(move)
        attacker_value = self._get_moving_piece_value(move)
        return victim_value >= attacker_value - 50  # Small tolerance
    
    def _capture_score(self, move) -> int:
        """Score for capture ordering (MVV-LVA)."""
        if not self._is_capture(move):
            return 0
        victim = self._get_captured_piece_value(move)
        attacker = self._get_moving_piece_value(move)
        return victim * 10 - attacker
    
    def _has_non_pawn_pieces(self, gs, is_white: bool) -> bool:
        """Check if side has non-pawn pieces (for null move pruning)."""
        color = "w" if is_white else "b"
        for row in range(8):
            for col in range(8):
                piece = gs.board[row][col]
                if piece.startswith(color) and piece[1] not in ['p', 'K']:
                    return True
        return False
    
    def _moves_equal(self, move1, move2) -> bool:
        """Check if two moves are equal."""
        if move1 is None or move2 is None:
            return False
        return str(move1) == str(move2)
    
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
    
    def _evaluate_fast(self, gs) -> int:
        """Ultra-fast evaluation function."""
        if gs.checkmate:
            return -CHECKMATE if gs.white_to_move else CHECKMATE
        elif gs.stalemate:
            return STALEMATE
        
        score = 0
        
        # Fast material count with simple positional bonuses
        for row in range(8):
            for col in range(8):
                piece = gs.board[row][col]
                if piece != "--":
                    color = piece[0]
                    piece_type = piece[1]
                    
                    if piece_type in piece_score:
                        material_value = piece_score[piece_type]
                        
                        # Simple positional bonus
                        positional_bonus = 0
                        if piece_type in piece_square_bonus:
                            # Center control bonus
                            center_distance = abs(3.5 - row) + abs(3.5 - col)
                            positional_bonus = piece_square_bonus[piece_type] * max(0, 4 - center_distance)
                        
                        total_value = material_value + positional_bonus
                        
                        if color == "w":
                            score += total_value
                        else:
                            score -= total_value
        
        return score

# Legacy compatibility functions
def find_random_move(valid_moves):
    """Return a random move from the list of valid moves."""
    if not valid_moves:
        return None
    return valid_moves[random.randint(0, len(valid_moves) - 1)]

def find_best_move_turbo(gs, valid_moves, return_queue, depth=10):
    """Turbo interface for legacy code."""
    ai = TurboChessAI(depth=depth, time_limit=30.0)
    best_move = ai.get_best_move(gs, use_iterative_deepening=True)
    return_queue.put(best_move)

# Quick usage function
def get_depth_10_move(gs, time_limit=30.0):
    """Quick function to get a depth 10 move."""
    ai = TurboChessAI(depth=10, time_limit=time_limit)
    return ai.get_best_move(gs, use_iterative_deepening=True)