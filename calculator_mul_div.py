#! /usr/bin/python3

def read_number(line, index):
  number = 0
  while index < len(line) and line[index].isdigit():
    number = number * 10 + int(line[index])
    index += 1
  if index < len(line) and line[index] == '.':
    index += 1
    keta = 0.1
    while index < len(line) and line[index].isdigit():
      number += int(line[index]) * keta
      keta /= 10
      index += 1
  token = {'type': 'NUMBER', 'number': number}
  return token, index


def read_multiply(line, index):
  token = {'type': 'MULTIPLY'}
  return token, index + 1


def read_divide(line, index):
  token = {'type': 'DIVIDE'}
  return token, index + 1


def read_plus(line, index):
  token = {'type': 'PLUS'}
  return token, index + 1


def read_minus(line, index):
  token = {'type': 'MINUS'}
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
    else:
      print('Invalid character found: ' + line[index])
      exit(1)
    tokens.append(token)
  return tokens


def evaluate(tokens):
  return evaluate_plus_and_minus(evaluate_multiply_and_divide(tokens))


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


def test(line):
  tokens = tokenize(line)
  actual_answer = evaluate(tokens)
  expected_answer = eval(line)
  if abs(actual_answer - expected_answer) < 1e-8:
    print("PASS! (%s = %f)" % (line, expected_answer))
  else:
    print("FAIL! (%s should be %f but was %f)" % (line, expected_answer, actual_answer))


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
  print("==== Test finished! ====\n")

run_test()

while True:
  print('> ', end="")
  line = input()
  tokens = tokenize(line)
  answer = evaluate(tokens)
  print("answer = %f\n" % answer)
