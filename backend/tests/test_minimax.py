import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from algorithms.minimax import best_move, winner
from algorithms.alpha_beta import best_move_alpha_beta

class TestAdversarial(unittest.TestCase):
    def test_win_detection(self):
        self.assertEqual(winner(["X","X","X","","","","","",""]), "X")
    def test_alpha_beta_immediate_win(self):
        board=["O","O","","X","X","","","",""]
        r=best_move_alpha_beta(board,7)
        self.assertEqual(r["move"],2)
    def test_both_algorithms_return_move(self):
        board=["","","","","","","","",""]
        self.assertIsNotNone(best_move(board,3)["move"])
        self.assertIsNotNone(best_move_alpha_beta(board,3)["move"])

    def test_minimax_prefers_faster_win(self):
        board=["O","O","","X","X","","","",""]
        minimax_result=best_move(board,7)
        alpha_result=best_move_alpha_beta(board,7)
        self.assertEqual(minimax_result["move"],2)
        self.assertEqual(minimax_result["score"],alpha_result["score"])
        self.assertGreater(minimax_result["nodes"],0)

    def test_alpha_beta_prunes_without_changing_the_best_score(self):
        board=["X","","","","","","","",""]
        minimax_result=best_move(board,7)
        alpha_result=best_move_alpha_beta(board,7)
        self.assertEqual(alpha_result["score"],minimax_result["score"])
        self.assertLess(alpha_result["nodes"],minimax_result["nodes"])
        self.assertGreater(alpha_result["pruned"],0)

if __name__=="__main__":
    unittest.main()
