import random
import math

class PlayerStats:
    def __init__(self):
        self.problems_attempted = 0
        self.problems_correct = 0
        self.incorrect_problems = []
        self.problem_types_stats = {
            'equation': {'attempted': 0, 'correct': 0},
            'sequence': {'attempted': 0, 'correct': 0},
            'logic': {'attempted': 0, 'correct': 0},
            'percentage': {'attempted': 0, 'correct': 0}
        }

    def add_problem_result(self, problem, is_correct):
        self.problems_attempted += 1
        if is_correct:
            self.problems_correct += 1
        else:
            self.incorrect_problems.append(problem)

        self.problem_types_stats[problem.problem_type]['attempted'] += 1
        if is_correct:
            self.problem_types_stats[problem.problem_type]['correct'] += 1

    def get_success_rate(self):
        if self.problems_attempted == 0:
            return 0
        return (self.problems_correct / self.problems_attempted) * 100

    def get_grade(self):
        success_rate = self.get_success_rate()
        if success_rate >= 90:
            return "Отлично (5)"
        elif success_rate >= 75:
            return "Хорошо (4)"
        elif success_rate >= 60:
            return "Удовлетворительно (3)"
        else:
            return "Неудовлетворительно (2)"

    def get_type_success_rate(self, problem_type):
        stats = self.problem_types_stats[problem_type]
        if stats['attempted'] == 0:
            return 0
        return (stats['correct'] / stats['attempted']) * 100


class MathProblem:
    def __init__(self, problem_type, condition, solution, difficulty, explanation=""):
        self.problem_type = problem_type
        self.condition = condition
        self.solution = solution
        self.difficulty = difficulty
        self.explanation = explanation

    def get_solution_text(self):
        return f"Правильный ответ: {self.solution}"

    def get_explanation(self):
        if self.explanation:
            return self.explanation
        if self.problem_type == 'equation':
            return f"Решение: {self.condition.replace('?', str(self.solution))}"
        elif self.problem_type == 'sequence':
            nums = self.condition.replace("Продолжи: ", "").split(", ")
            for i, num in enumerate(nums):
                if num == "?":
                    return f"Пропущенное число: {self.solution}. Это арифметическая/геометрическая прогрессия."
        elif self.problem_type == 'percentage':
             return f"Это задача на проценты. Ответ: {self.solution}"
        return "Правильный ответ указан выше"
    
class MathProblemGenerator:
    def __init__(self):
        self.used_problems = set()

    @staticmethod
    def generate_problem(difficulty):
        types_available = ['addition', 'subtraction']
        if difficulty >= 2:
            types_available.extend(['multiplication', 'sequence'])
        if difficulty >= 3:
            types_available.extend(['division', 'percentage'])
        if difficulty >= 4:
            types_available.extend(['equation'])

        ptype = random.choice(types_available)

        if ptype == 'addition':
            a = random.randint(10 * difficulty, 30 * difficulty)
            b = random.randint(10 * difficulty, 30 * difficulty)
            return MathProblem('equation', f"Реши: {a} + {b} = ?", a + b, difficulty, f"Складываем {a} и {b}, получаем {a + b}.")
        elif ptype == 'subtraction':
            a = random.randint(20 * difficulty, 40 * difficulty)
            b = random.randint(5 * difficulty, a)
            return MathProblem('equation', f"Реши: {a} - {b} = ?", a - b, difficulty, f"Вычитаем {b} из {a}, получаем {a - b}.")
        elif ptype == 'multiplication':
            a = random.randint(2 + difficulty, 8 + difficulty * 2)
            b = random.randint(2 + difficulty, 8 + difficulty * 2)
            return MathProblem('equation', f"Реши: {a} * {b} = ?", a * b, difficulty, f"Умножаем {a} на {b}, получаем {a * b}.")
        elif ptype == 'division':
            b = random.randint(2 + difficulty, 8 + difficulty)
            res = random.randint(2 + difficulty, 10 + difficulty * 2)
            a = b * res
            return MathProblem('equation', f"Реши: {a} / {b} = ?", res, difficulty, f"Делим {a} на {b}, получаем {res}.")
        elif ptype == 'sequence':
            start = random.randint(1, 10 * difficulty)
            step = random.randint(2, 4 + difficulty)
            missing = start + 3 * step
            seq = f"{start}, {start + step}, {start + 2 * step}, ?, {start + 4 * step}"
            return MathProblem('sequence', f"Продолжи: {seq}", missing, difficulty, f"Шаг прогрессии равен {step}. Значит {start + 2*step} + {step} = {missing}.")
        elif ptype == 'percentage':
            total = random.choice([50, 100, 150, 200, 250, 300, 400, 500, 600, 800, 1000])
            percent = random.choice([5, 10, 15, 20, 25, 30, 40, 50, 75])
            res = int(total * percent / 100)
            return MathProblem('percentage', f"Найди {percent}% от {total}", res, difficulty, f"Чтобы найти {percent}%, нужно {total} умножить на {percent} и разделить на 100. ({total} * {percent} / 100 = {res}).")
        elif ptype == 'equation':
            x = random.randint(2, 10 + difficulty * 2)
            mult = random.randint(2, 5 + difficulty)
            return MathProblem('equation', f"Найди X: {mult} * X = {mult * x}", x, difficulty, f"Чтобы найти X, делим {mult*x} на {mult}, получаем {x}.")