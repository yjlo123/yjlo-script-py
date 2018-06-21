from lexer import Lexer
from parser import Parser
from evaluator import init_env, evaluate

try:
	lexer = Lexer()
	tokens = lexer.tokenize('9+2.2*2')
	parser = Parser()
	ast = parser.parse(tokens)
	print('==== AST ====\n%s' % ast)
	result = evaluate(ast, init_env())
	print('==== RESULT ====\n%s' % result)
except EvalExeption as e:
	print('[ERROR]' + str(e))
except KeyboardInterrupt:
	print('\nInterrupted')
