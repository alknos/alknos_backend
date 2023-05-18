
def convert_equation(equation: str) -> str:
    subscripts = {'₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'}
    for subscript, replacement in subscripts.items():
        equation = equation.replace(subscript, replacement)
    new_equation = ""
    for i in range(len(equation)):
        if equation[i].isdigit() and equation[i] == '1':
            if i > 0 and i < len(equation)-1:
                if not equation[i-1].isdigit() and not equation[i+1].isdigit():
                    continue
                if i > 1 and equation[i-1].isspace() and not equation[i+1].isdigit():
                    continue
                if i > 1 and equation[i+1].isspace() and not equation[i-1].isdigit():
                    continue
            else:
                if i == 0 and not equation[i+1].isdigit():
                    continue
                if i == len(equation)-1 and not equation[i-1].isdigit():
                    continue
        new_equation += equation[i]
    return new_equation