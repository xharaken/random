#! /usr/bin/python3
# Run this program with python3 (not python2)

def read_number(line, index):
    number = 0
    flag = 0
    keta = 1
    while index < len(line) and (line[index].isdigit() or line[index] == '.'):
        if line[index] == '.':
            flag = 1
        else:
            number = number * 10 + int(line[index])
            if flag == 1:
                keta *= 0.1
        index += 1
    token = {'type': 'NUMBER', 'number': float(number * keta)}
    return token, index


def read_plus(line, index):
    token = {'type': 'PLUS'}
    return token, index + 1


def read_minus(line, index):
    token = {'type': 'MINUS'}
    return token, index + 1


def read_multiply(line, index):
    token = {'type': 'MULTIPLY'}
    return token, index + 1


def read_divide(line, index):
    token = {'type': 'DIVIDE'}
    return token, index + 1


def read_left(line, index):
    token = {'type': 'LEFT'}
    return token, index + 1


def read_right(line, index):
    token = {'type': 'RIGHT'}
    return token, index + 1


def tokenize(line):
    tokens = []
    index = 0
    while index < len(line):
        if line[index].isdigit():
            (token, index) = read_number(line, index)
        elif line[index] == '+':
            (token, index) = read_plus(line, index)
        elif line[index] == '-':
            (token, index) = read_minus(line, index)
        elif line[index] == '*':
            (token, index) = read_multiply(line, index)
        elif line[index] == '/':
            (token, index) = read_divide(line, index)
        elif line[index] == '(':
            (token, index) = read_left(line, index)
        elif line[index] == ')':
            (token, index) = read_right(line, index)
        else:
            print('Invalid character found: ' + line[index])
            exit(1)
        tokens.append(token)
    return tokens


def evaluate_brackets(tokens):
    index = 0
    bracket_left_index = 0
    while index < len(tokens):
        # Find the right most ')'
        if tokens[index]['type'] == 'RIGHT':
            for i in reversed(range(0, index)):
                # Find the corresponding '('
                if tokens[i]['type'] == 'LEFT':
                    left_index = i
                    break

            # Evaluate an expression inside the bracket
            value = evaluate(tokens[left_index + 1 : index])
            tokens[index] = {'type': 'NUMBER', 'number': value}
            del tokens[left_index : index]
            index = left_index
        index += 1
    return tokens


def evaluate_multiply_and_divide(tokens):
    index = 0
    while index < len(tokens):
        if tokens[index]['type'] == 'MULTIPLY':
            num = tokens[index - 1]['number'] * tokens[index + 1]['number']
            del tokens[index - 1 : index + 2]
            tokens.insert(index - 1, {'type': 'NUMBER', 'number': num})
        elif tokens[index]['type'] == 'DIVIDE':
            num = tokens[index - 1]['number'] * 1.0 / tokens[index + 1]['number']
            del tokens[index - 1 : index + 2]
            tokens.insert(index - 1, {'type': 'NUMBER', 'number': num})
        else:
            index += 1
    return tokens


def evaluate_plus_and_minus(tokens):
    answer = 0
    tokens.insert(0, {'type': 'PLUS'}) # Insert a dummy '+' token
    index = 1
    while index < len(tokens):
        if tokens[index]['type'] == 'NUMBER':
            if tokens[index - 1]['type'] == 'PLUS':
                answer += tokens[index]['number']
            elif tokens[index - 1]['type'] == 'MINUS':
                answer -= tokens[index]['number']
            else:
                print('Invalid syntax')
                exit(1)
        index += 1
    return answer


def evaluate(tokens):
    tokens = evaluate_brackets(tokens)
    tokens = evaluate_multiply_and_divide(tokens)
    return evaluate_plus_and_minus(tokens)


def test(line):
    tokens = tokenize(line)
    actual_answer = evaluate(tokens)
    expected_answer = eval(line)
    if abs(actual_answer - expected_answer) < 1e-8:
        print("PASS! (%s = %f)" % (line, expected_answer))
    else:
        print("FAIL! (%s should be %f but was %f)" % (
            line, expected_answer, actual_answer))


# Add more tests to this function :)
def run_test():
    print("==== Test started! ====")
    test("1")
    test("11")
    test("2+3")
    test("2-3")
    test("2*3")
    test("2/3")
    test("2+3+4")
    test("2-3-4")
    test("2*3+4")
    test("2+3*4")
    test("2/3+4")
    test("2+3/4")
    test("2*3-4*5-6/7+8/9")
    test("11.1")
    test("1.1+2.2")
    test("1.1-2.2")
    test("1.1*2.2")
    test("1.1/2.2")
    test("1.1*2.2-3.3*4.4-5.5/6.6+7.7/8.8")
    test("(1)")
    test("(1+2)")
    test("((1))")
    test("((1.1))")
    test("(1+2)*3")
    test("(1+2)/3")
    test("1*(2+3)")
    test("1/(2+3)")
    test("(1+2)*(3+4)")
    test("(1+2)/(3+4)")
    test("1-(2-3)")
    test("1-(2-(3-4))")
    test("1-(2-(3-(4-5)))")
    test("1-(2-(3-(4-5)-6))")
    test("1-(2-(3-(4-5)-6))")
    test("1-(2-(3-(4-5)-6)-7)")
    test("1-(2-(3-(4-5)-6)-7)-8")
    test("(1+2)*3-4/(5-(6-7*8+9/(10-11)*12))")
    test("(1.1+2.2)*3.3-4.4/(5.5-(6.5-7.7*8.8+9.9/(10.0-11.1)*12.2))")
    print("==== Test finished! ====\n")

run_test()

while True:
    print('> ', end="")
    line = input()
    tokens = tokenize(line)
    answer = evaluate(tokens)
    print("answer = %f\n" % answer)
