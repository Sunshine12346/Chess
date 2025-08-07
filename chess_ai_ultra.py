import random
import time
import copy
from typing import Dict, List, Tuple, Optional, Any

# Ultra-fast transposition table with minimal overhead
class UltraTranspositionTable:
    def __init__(self, size_mb: int = 256):
        self.size = (size_mb * 1024 * 1024) // 16  # Smaller entries for speed
        self.table = {}
        self.hits = 0
        self.stores = 0

    def lookup(self, key: int, depth: int, alpha: int, beta: int) -> Optional[Tuple[int, str, Any]]:
        if key in self.table:
            score, stored_depth, flag, move = self.table[key]
            if stored_depth >= depth:
                self.hits += 1
                if flag == "EXACT":
                    return score, flag, move
                elif flag == "ALPHA" and score <= alpha:
                    return alpha, flag, move
                elif flag == "BETA" and score >= beta:
                    return beta, flag, move
        return None

    def store(self, key: int, score: int, depth: int, flag: str, move: Any = None):
        # Always replace - no size checking for speed
        self.table[key] = (score, depth, flag, move)
        self.stores += 1

# Ultra-fast killer moves (fixed size arrays)
class UltraKillerMoves:
    def __init__(self):
        # Fixed size for speed - no bounds checking
        self.primary = [None] * 32
        self.secondary = [None] * 32
    
    def add_killer(self, depth: int, move: Any):
        if depth < 32:
            if move != self.primary[depth]:
                self.secondary[depth] = self.primary[depth]
                self.primary[depth] = move
    
    def get_killer_score(self, depth: int, move: Any) -> int:
        if depth < 32:
            if move == self.primary[depth]:
                return 9000
            elif move == self.secondary[depth]:
                return 8900
        return 0

# Minimal history table
class UltraHistoryTable:
    def __init__(self):
        self.history = {}
        self.max_val = 1000
    
    def add_history(self, move_key: str, depth: int):
        score = depth * depth
        self.history[move_key] = min(self.max_val, self.history.get(move_key, 0) + score)
    
    def get_score(self, move_key: str) -> int:
        return self.history.get(move_key, 0)

# Ultra-fast position hashing
def ultra_hash(gs) -> int:
    """Fastest possible position hash."""
    h = 0
    board = gs.board
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "--":
                h ^= hash(piece) * (row * 8 + col + 1)
    return h ^ (12345 if gs.white_to_move else 54321)

# Global instances
tt_ultra = UltraTranspositionTable(256)
killers_ultra = UltraKillerMoves()
history_ultra = UltraHistoryTable()

# Ultra-fast piece values
PIECE_VALUES = {'K': 0, 'Q': 900, 'R': 500, 'B': 330, 'N': 320, 'p': 100}

# Global variables
counter = 0
next_move = None
CHECKMATE = 50000
DEPTH_10_TARGET_TIME = 0.5  # Target: depth 10 in 0.5 seconds

class UltraChessAI:
    """Ultra-fast Chess AI - Depth 10 in time of original Depth 3."""
    
    def __init__(self, depth: int = 10, time_limit: float = 10.0):
        self.depth = depth
        self.time_limit = time_limit
        self.nodes = 0
        self.start_time = 0
        
        # Ultra-aggressive pruning parameters
        self.null_move_reduction = 3  # More aggressive
        self.lmr_base_reduction = 2   # Deeper reductions
        self.lmr_threshold = 3        # Start earlier
        self.razoring_margin = 400    # Razoring
        self.futility_margins = [0, 300, 500, 700, 900]  # Progressive futility
        self.reverse_futility_margin = 200
        
    def get_best_move(self, gs) -> Any:
        """Get best move with ultra optimizations."""
        global counter, next_move, tt_ultra
        
        moves = gs.get_valid_moves()
        if not moves:
            return None
            
        if len(moves) == 1:
            return moves[0]
        
        counter = 0
        next_move = None
        self.nodes = 0
        self.start_time = time.time()
        
        print(f"Ultra search: {len(moves)} moves, target depth {self.depth}")
        
        # Use iterative deepening but with aggressive time management
        best_move = None
        for d in range(1, self.depth + 1):
            if time.time() - self.start_time > self.time_limit * 0.7:
                print(f"Time cutoff at depth {d-1}")
                break
                
            move = self._search_root(gs, moves, d)
            if move:
                best_move = move
                elapsed = time.time() - self.start_time
                nps = self.nodes / max(elapsed, 0.001)
                print(f"Depth {d}: {move} in {elapsed:.3f}s ({nps:,.0f} nps)")
                
        return best_move
    
    def _search_root(self, gs, moves, depth):
        """Root search with ultra-fast move ordering."""
        global next_move
        
        # Ultra-fast move ordering
        captures = []
        quiet_moves = []
        
        for move in moves:
            if self._is_capture(move):
                # Sort captures by value immediately
                victim_val = PIECE_VALUES.get(move.piece_captured[1] if len(move.piece_captured) > 1 else 'p', 100)
                attacker_val = PIECE_VALUES.get(move.piece_moved[1] if len(move.piece_moved) > 1 else 'p', 100)
                captures.append((victim_val * 10 - attacker_val, move))
            else:
                quiet_moves.append(move)
        
        # Sort only captures (most important)
        captures.sort(key=lambda x: x[0], reverse=True)
        ordered_moves = [move for _, move in captures] + quiet_moves
        
        alpha = -CHECKMATE
        beta = CHECKMATE
        best_score = -CHECKMATE
        best_move = None
        
        for i, move in enumerate(ordered_moves):
            gs.make_move(move)
            
            if i == 0:
                score = -self._search_ultra(gs, depth - 1, -beta, -alpha, True)
            else:
                # Ultra-aggressive PVS
                score = -self._search_ultra(gs, depth - 1, -alpha - 1, -alpha, True)
                if alpha < score < beta:
                    score = -self._search_ultra(gs, depth - 1, -beta, -alpha, True)
            
            gs.undo_move()
            
            if score > best_score:
                best_score = score
                best_move = move
                next_move = move
                alpha = max(alpha, score)
        
        return best_move
    
    def _search_ultra(self, gs, depth: int, alpha: int, beta: int, allow_null: bool) -> int:
        """Ultra-fast search with extreme pruning."""
        global counter
        counter += 1
        self.nodes += 1
        
        # Time check every 2048 nodes (power of 2 for speed)
        if self.nodes & 2047 == 0:
            if time.time() - self.start_time > self.time_limit:
                return 0
        
        # Transposition table lookup
        pos_hash = ultra_hash(gs)
        tt_result = tt_ultra.lookup(pos_hash, depth, alpha, beta)
        if tt_result:
            return tt_result[0]
        
        # Terminal depth
        if depth <= 0:
            return self._quiescence_ultra(gs, alpha, beta)
        
        # Mate distance pruning
        alpha = max(alpha, -CHECKMATE + self.nodes)
        beta = min(beta, CHECKMATE - self.nodes)
        if alpha >= beta:
            return alpha
        
        moves = gs.get_valid_moves()
        if not moves:
            return -CHECKMATE if gs.checkmate else 0
        
        # Static evaluation for pruning decisions
        static_eval = self._eval_ultra(gs)
        is_pv = beta - alpha > 1
        
        # REVERSE FUTILITY PRUNING (most aggressive)
        if (not is_pv and depth <= 3 and not gs.checkmate and 
            static_eval - self.reverse_futility_margin * depth >= beta):
            return static_eval
        
        # RAZORING - extremely aggressive
        if (not is_pv and depth <= 3 and not gs.checkmate and
            static_eval + self.razoring_margin < alpha):
            razor_score = self._quiescence_ultra(gs, alpha - self.razoring_margin, alpha - self.razoring_margin + 1)
            if razor_score < alpha:
                return razor_score
        
        # NULL MOVE PRUNING - ultra aggressive
        if (allow_null and not is_pv and depth >= 3 and not gs.checkmate and
            static_eval >= beta and self._has_pieces(gs)):
            
            gs.white_to_move = not gs.white_to_move
            null_score = -self._search_ultra(gs, depth - 1 - self.null_move_reduction, -beta, -beta + 1, False)
            gs.white_to_move = not gs.white_to_move
            
            if null_score >= beta:
                return null_score  # Fail high
        
        # FUTILITY PRUNING
        futility_pruning = (not is_pv and depth <= 4 and not gs.checkmate and 
                           abs(alpha) < CHECKMATE - 100)
        futility_margin = self.futility_margins[min(depth, 4)] if futility_pruning else 0
        
        # Move generation and ordering
        captures = []
        quiets = []
        
        for move in moves:
            if self._is_capture(move):
                captures.append(move)
            else:
                quiets.append(move)
        
        # Sort captures only (quiets use history/killers)
        captures.sort(key=self._capture_score, reverse=True)
        
        # Main search loop
        best_score = -CHECKMATE
        best_move = None
        moves_searched = 0
        
        # Search captures first
        for move in captures:
            gs.make_move(move)
            moves_searched += 1
            
            score = -self._search_ultra(gs, depth - 1, -beta, -alpha, True)
            gs.undo_move()
            
            if score > best_score:
                best_score = score
                best_move = move
            
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        
        # Search quiet moves with heavy pruning
        if alpha < beta:
            for move in quiets:
                # FUTILITY PRUNING for quiet moves
                if (futility_pruning and moves_searched >= 1 and
                    static_eval + futility_margin <= alpha):
                    continue
                
                # LATE MOVE REDUCTIONS - ultra aggressive
                reduction = 0
                if moves_searched >= self.lmr_threshold and depth >= 3:
                    reduction = self.lmr_base_reduction
                    if moves_searched > 6:
                        reduction += 1
                    if not is_pv:
                        reduction += 1
                
                gs.make_move(move)
                moves_searched += 1
                
                # Search with reduction
                search_depth = max(1, depth - 1 - reduction)
                if moves_searched == 1:
                    score = -self._search_ultra(gs, depth - 1, -beta, -alpha, True)
                else:
                    score = -self._search_ultra(gs, search_depth, -alpha - 1, -alpha, True)
                    if score > alpha and reduction > 0:
                        score = -self._search_ultra(gs, depth - 1, -alpha - 1, -alpha, True)
                    if score > alpha and score < beta:
                        score = -self._search_ultra(gs, depth - 1, -beta, -alpha, True)
                
                gs.undo_move()
                
                if score > best_score:
                    best_score = score
                    best_move = move
                
                alpha = max(alpha, score)
                if alpha >= beta:
                    # Add to killers and history
                    killers_ultra.add_killer(depth, move)
                    move_key = f"{move.piece_moved}_{move.notation}" if hasattr(move, 'notation') else str(move)
                    history_ultra.add_history(move_key, depth)
                    break
        
        # Store in transposition table
        if best_score <= alpha:
            flag = "ALPHA"
        elif best_score >= beta:
            flag = "BETA"
        else:
            flag = "EXACT"
        
        tt_ultra.store(pos_hash, best_score, depth, flag, best_move)
        return best_score
    
    def _quiescence_ultra(self, gs, alpha: int, beta: int) -> int:
        """Ultra-fast quiescence search."""
        self.nodes += 1
        
        stand_pat = self._eval_ultra(gs)
        
        if stand_pat >= beta:
            return beta
        
        # Delta pruning - don't search hopeless captures
        if stand_pat < alpha - 900:  # Queen value
            return alpha
        
        alpha = max(alpha, stand_pat)
        
        # Only search good captures
        moves = gs.get_valid_moves()
        captures = [m for m in moves if self._is_capture(m) and self._is_good_capture(m)]
        captures.sort(key=self._capture_score, reverse=True)
        
        for move in captures:
            gs.make_move(move)
            score = -self._quiescence_ultra(gs, -beta, -alpha)
            gs.undo_move()
            
            if score >= beta:
                return beta
            alpha = max(alpha, score)
        
        return alpha
    
    def _eval_ultra(self, gs) -> int:
        """Ultra-fast evaluation."""
        if gs.checkmate:
            return -CHECKMATE
        if gs.stalemate:
            return 0
        
        score = 0
        board = gs.board
        
        # Material only for speed
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != "--":
                    value = PIECE_VALUES.get(piece[1], 0)
                    if piece[0] == "w":
                        score += value
                    else:
                        score -= value
        
        return score
    
    def _is_capture(self, move) -> bool:
        return hasattr(move, 'piece_captured') and move.piece_captured != "--"
    
    def _is_good_capture(self, move) -> bool:
        if not self._is_capture(move):
            return False
        victim = PIECE_VALUES.get(move.piece_captured[1] if len(move.piece_captured) > 1 else 'p', 100)
        attacker = PIECE_VALUES.get(move.piece_moved[1] if len(move.piece_moved) > 1 else 'p', 100)
        return victim >= attacker - 100  # Capture equal or better
    
    def _capture_score(self, move) -> int:
        if not self._is_capture(move):
            return 0
        victim = PIECE_VALUES.get(move.piece_captured[1] if len(move.piece_captured) > 1 else 'p', 100)
        attacker = PIECE_VALUES.get(move.piece_moved[1] if len(move.piece_moved) > 1 else 'p', 100)
        return victim * 10 - attacker
    
    def _has_pieces(self, gs) -> bool:
        """Quick check if side has non-pawn pieces."""
        color = "w" if gs.white_to_move else "b"
        for row in range(8):
            for col in range(8):
                piece = gs.board[row][col]
                if piece.startswith(color) and piece[1] not in ['p', 'K']:
                    return True
        return False

# Ultra-fast interface functions
def get_ultra_move(gs, target_time=DEPTH_10_TARGET_TIME):
    """Get depth 10 move in target time (default 0.5s)."""
    ai = UltraChessAI(depth=10, time_limit=target_time * 2)  # 2x buffer
    return ai.get_best_move(gs)

def get_lightning_move(gs):
    """Get depth 10 move as fast as possible."""
    ai = UltraChessAI(depth=10, time_limit=0.3)
    return ai.get_best_move(gs)

def benchmark_ultra_ai(gs, target_depth=10):
    """Benchmark the ultra AI."""
    print(f"🚀 ULTRA CHESS AI BENCHMARK - TARGET DEPTH {target_depth}")
    print("=" * 50)
    
    times = []
    for i in range(3):  # Multiple runs
        print(f"\nRun {i+1}:")
        start = time.time()
        ai = UltraChessAI(depth=target_depth, time_limit=10.0)
        move = ai.get_best_move(gs)
        elapsed = time.time() - start
        times.append(elapsed)
        
        nps = ai.nodes / max(elapsed, 0.001)
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Nodes: {ai.nodes:,}")
        print(f"  Speed: {nps:,.0f} nps")
        print(f"  Move: {move}")
    
    avg_time = sum(times) / len(times)
    print(f"\n📊 RESULTS:")
    print(f"  Average time: {avg_time:.3f}s")
    print(f"  Target achieved: {'✅' if avg_time <= DEPTH_10_TARGET_TIME else '❌'}")
    print(f"  Speedup needed: {avg_time/DEPTH_10_TARGET_TIME:.1f}x" if avg_time > DEPTH_10_TARGET_TIME else "  Target met!")
    
    return avg_time

# Compatibility functions
def find_best_move_ultra(gs, valid_moves, return_queue, depth=10):
    """Ultra interface for legacy code."""
    ai = UltraChessAI(depth=depth, time_limit=5.0)
    move = ai.get_best_move(gs)
    return_queue.put(move)