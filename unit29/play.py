"""unit29/tetris.py の Board で遊ぶ、文字のテトリス。キーを打って Enter で確定する。"""
import random

from tetris import Board, SHAPES

HELP = "a=左 d=右 w=回す s=1段下げる x=一気に落とす q=やめる（ほかのキー・Enter だけ=1段下げる）"


def show(board):
    print(board.render())
    print(f"消した行: {board.lines}")


def main():
    board = Board()
    board.spawn(random.choice(list(SHAPES)))

    while not board.game_over:
        show(board)
        key = input(HELP + "\n> ").strip().lower()
        print()

        if key == "q":
            print("終了しました")
            return
        if key == "a":
            board.move(-1)
        elif key == "d":
            board.move(1)
        elif key == "w":
            board.rotate()
        elif key == "x":
            board.hard_drop()
        else:
            board.step()

        # ブロックが固定されたら、次のブロックを出す
        if not board.piece_cells():
            board.spawn(random.choice(list(SHAPES)))

    show(board)
    print("ゲームオーバー")


if __name__ == "__main__":
    main()
