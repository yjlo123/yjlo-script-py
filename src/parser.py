from lexer import Lexer, TokenType

class Parser(object):
	PRECEDENCE = {
		15: ['[','.'],
		14: ['**'],
		13: ['_-','_!','_~','++','--','_--'],
		12: ['*','/','/.','%'],
		11: ['+','-'],
		10: ['<<','>>','>>>'],
		9: ['<','<=','>','>+'],
		8: ['==','!='],
		7: ['&'],
		6: ['^'],
		5: ['|'],
		4: ['&&'],
		3: ['||'],
		2: ['?', ':'],
		1: [','],
		0: ['=',':='],
	}

	def __init__(self):
		self.tokens = []
		self.len = 0	# num of tokens
		self.i = -1		# index
		self.t = None	# current token
		self.n = None	# next token

	def init_tokens(self, tokens):
		self.tokens = tokens
		self.len = len(tokens)
		self.skip()

	def get_precedence(self, operator):
		for key, value in self.PRECEDENCE.items():
			if value in value:
				return key
		return -1

	''' Advance Token '''
	def advance(self, token_type=None, value=None):
		self.ignore_newline()
		if value and not self.check(token_type, value):
			raise Exception('[Parser] token error')
		self.skip()

	def advance_optional(self, token_type, value):
		if self.check(token_type, value):
			advance(token_type, value)

	def check(self, token_type, value=None):
		self.ignore_newline()
		return (self.t and self.t.type == token_type
			and ( self.t.value == value if value else True))

	def check_operator(self, value=None):
		return self.check(TokenType.OPERATOR, value)

	def check_name(self, value=None):
		return self.check(TokenType.NAME, value)

	def reach_eof(self):
		return self.check(TokenType.EOF)

	def ignore_newline(self):
		if self.i >= self.len:
			token = None
		elif self.t.type == TokenType.NEWLINE:
			self.skip()

	def skip(self):
		self.i += 1
		self.t = self.tokens[self.i]
		if self.reach_eof():
			self.n = None
		else:
			self.n = self.tokens[self.i+1]

	''' AST '''
	def expr(self):
		prev = None
		node = None
		infix = []
		while not self.reach_eof():
			if self.t.type == TokenType.NEWLINE:
				self.skip()
				# TODO
				break
			prev = self.t
			# TODO check expr terminator
			# TODO bracket
			if self.check_name():
				# TODO
				pass
			elif self.check(TokenType.STRING) or self.check(TokenType.NUMBER):
				node = {
					'tag': 'constant',
					'value': self.t.value,
					'line': self.t.line,
				}
			elif self.check_name():
				node = {
					'tag': 'variable',
					'name': self.t.value,
					'type': 'variable',
					'line': self.t.line,
				}
			elif self.check_operator():
				node = {
					'tag': 'variable',
					'name': self.t.value,
					'type': 'operator',
					'line': self.t.line,
				}
			else:
				raise Exception('[Parser] Unsupported expression token')
			infix.append(node)
			self.advance()
		# print(infix)
		
		# in-fix to post-fix
		postfix = []
		temp_stack = []
		for node in infix:
			if node['tag'] == 'variable' and node['type'] == 'variable':
				postfix.append(node)
			elif node['tag'] == 'constant':
				postfix.append(node['value'])
			else:
				# operator
				# TODO unary & increment/decrement
				while len(temp_stack) > 0 and self.get_precedence(node['name']) <= self.get_precedence(temp_stack[-1]['name']):
					postfix.append(temp_stack.pop())
				temp_stack.append(node)
		while len(temp_stack) > 0:
			postfix.append(temp_stack.pop())
		if len(postfix) == 1:
			return postfix[0]

		# print(postfix)
		# build AST
		ast_stack = []
		for node in postfix:
			if isinstance(node, dict) and node['tag'] == 'variable' and node['type'] == 'operator':
				operands = []
				operands = [ast_stack.pop()] + operands
				operands = [ast_stack.pop()] + operands
				apply_node = {
					'tag': 'application',
					'operator': node,
					'operands': operands,
					'line': node['line'],
				}
				ast_stack.append(apply_node)
			else:
				ast_stack.append(node)
		return ast_stack[0]

	def stmt(self):
		ast = None
		if self.check_operator(';'):
			self.advance()
		elif self.check_name('var'):
			self.advance()
			pass
		else:
			ast = self.expr()
		self.advance_optional(TokenType.OPERATOR, ';')
		return ast

	def stmt_list(self):
		stmts = []
		while True:
			self.ignore_newline()
			if (self.reach_eof()
				or self.check_operator('}')
				or self.check_name('case')
				or self.check_name('default')):
				break
			stmt = self.stmt()
			if stmt:
				stmts.append(stmt)
		return stmts or None

	def parse(self, tokens):
		self.init_tokens(tokens)
		print('==== TOKENS ====')
		for t in self.tokens:
			print(t)
		return self.stmt_list()

def main():
	lexer = Lexer()
	tokens = lexer.tokenize('1+2')
	parser = Parser()
	ast = parser.parse(tokens)
	print(ast)

if __name__ == '__main__':
	main()