import utils

board = utils.Board(10, 10)

while True:
    print(board)
    x, y = map(int, input("Enter x, y: ").split())
    point = utils.Point(x, y)
    action = input("Enter action: ")
    if action == "r":
        board.reveal(point)
    elif action == "f":
        board.flag(point)
    elif action == "u":
        board.unflag(point)
    else:
        break