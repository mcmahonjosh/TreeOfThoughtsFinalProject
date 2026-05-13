def get_task(name):
    if name == 'game24':
        from tot.tasks.game24 import Game24Task
        return Game24Task()
    elif name == 'text':
        from tot.tasks.text import TextTask
        return TextTask()
    elif name == 'crosswords':
        from tot.tasks.crosswords import MiniCrosswordsTask
        return MiniCrosswordsTask()
    elif name == 'sudoku':
        from tot.tasks.sudoku import SudokuTask
        return SudokuTask()
    elif name == 'sudoku4x4':
        from tot.tasks.sudoku4x4 import Sudoku4x4Task
        return Sudoku4x4Task()
    else:
        raise NotImplementedError
