from .minimax import available_moves, winner, terminal_score

def alpha_beta(board, depth, alpha, beta, is_max, ai="O", human="X", trace=None):
    if trace is not None:
        trace["nodes"] += 1
    w = winner(board)
    if w or depth == 0 or not available_moves(board):
        return terminal_score(board, depth, ai, human)
    if is_max:
        value = -1000
        moves = available_moves(board)
        for index, move in enumerate(moves):
            board[move] = ai
            value = max(value, alpha_beta(board, depth-1, alpha, beta, False, ai, human, trace))
            board[move] = ""
            alpha = max(alpha, value)
            if alpha >= beta:
                if trace is not None: trace["pruned"] += len(moves) - index - 1
                break
        return value
    value = 1000
    moves = available_moves(board)
    for index, move in enumerate(moves):
        board[move] = human
        value = min(value, alpha_beta(board, depth-1, alpha, beta, True, ai, human, trace))
        board[move] = ""
        beta = min(beta, value)
        if alpha >= beta:
            if trace is not None: trace["pruned"] += len(moves) - index - 1
            break
    return value

def best_move_alpha_beta(board, depth, ai="O", human="X"):
    trace = {"nodes": 0, "pruned": 0}
    best_score, move = -1000, None
    evaluated_moves = []
    for candidate in available_moves(board):
        board[candidate] = ai
        score = alpha_beta(board, depth-1, -1000, 1000, False, ai, human, trace)
        board[candidate] = ""
        evaluated_moves.append({"move": candidate, "score": score})
        if score > best_score:
            best_score, move = score, candidate
    return {
        "move": move,
        "score": best_score,
        "nodes": trace["nodes"],
        "pruned": trace["pruned"],
        "evaluated_moves": evaluated_moves,
    }
