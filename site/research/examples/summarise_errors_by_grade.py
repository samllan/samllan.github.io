"""Break held-out grading errors down by ordinal reference level."""
from collections import defaultdict
from statistics import mean


def error_by_grade(predictions):
    errors = defaultdict(list)
    for reference, predicted in predictions:
        errors[reference].append(predicted - reference)
    return [
        (grade, len(values), mean(values), mean(map(abs, values)))
        for grade, values in sorted(errors.items())
    ]


if __name__ == "__main__":
    print("grade,count,signed_error,absolute_error")
    for row in error_by_grade([(0, 0.7), (0, 0.2), (1, 1.2), (3, 2.1), (3, 2.8)]):
        print(*row, sep=",")
