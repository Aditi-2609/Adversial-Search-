WIN_LINES = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))

def winner(board):
    for a,b,c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None

def evaluate(board, ai="O", human="X"):
    w = winner(board)
    if w == ai: return 10
    if w == human: return -10
    return 0

def terminal_score(board, depth, ai="O", human="X"):
    result = evaluate(board, ai, human)
    if result > 0:
        return result + depth
    if result < 0:
        return result - depth
    return 0

def available_moves(board):
    return [i for i, v in enumerate(board) if v == ""]

def minimax(board, depth, is_max, ai="O", human="X", trace=None):
    if trace is not None:
        trace["nodes"] += 1
    w = winner(board)
    if w or depth == 0 or not available_moves(board):
        return terminal_score(board, depth, ai, human)
    if is_max:
        best = -1000
        for move in available_moves(board):
            board[move] = ai
            best = max(best, minimax(board, depth-1, False, ai, human, trace))
            board[move] = ""
        return best
    best = 1000
    for move in available_moves(board):
        board[move] = human
        best = min(best, minimax(board, depth-1, True, ai, human, trace))
        board[move] = ""
    return best

def best_move(board, depth, ai="O", human="X"):
    trace = {"nodes": 0, "pruned": 0}
    best_score, move = -1000, None
    evaluated_moves = []
    for candidate in available_moves(board):
        board[candidate] = ai
        score = minimax(board, depth-1, False, ai, human, trace)
        board[candidate] = ""
        evaluated_moves.append({"move": candidate, "score": score})
        if score > best_score:
            best_score, move = score, candidate
    return {
        "move": move,
        "score": best_score,
        "nodes": trace["nodes"],
        "pruned": 0,
        "evaluated_moves": evaluated_moves,
    }
