class TokenType():
	NEWLINE = 'newline'
	EOF = 'eof'
	NAME = 'name'
	NUMBER = 'number'
	STRING = 'string'
	OPERATOR = 'operator'

class Token():
	def __init__(self, t, value=None, line=-1):
		self.type = t
		self.value = value
		self.line = line

	def __str__(self):
		return '({0})[{1}]	{2}'.format(self.line, self.type, str(self.value))

ESC_CHAR = {
	'b': '\b',
	'f': '\f',
	'n': '\n',
	'r': '\r',
	't': '\t',
}

class Lexer():
	def __init__(self):
		self.tokens = []
		self.line = 1
		self.i = -1
		self.s = None
		self.len = -1
		self.c = None
		self.next = None

	def init_source(self, source):
		self.s = source
		self.len = len(source)

	def add(self, token_type, value):
		self.tokens.append(Token(token_type, value, self.line))

	def advance(self):
		if self.has_next():
			self.i += 1
			self.c = self.s[self.i]
			if self.has_next():
				self.next = self.s[self.i+1]
			else:
				self.next = None
		else:
			self.c = self.next
			self.next = None

	def has_next(self):
		return self.i + 1 < self.len

	def tokenize(self, source):
		self.init_source(source)
		self.advance()
		while self.c is not None:
			# new line
			if self.c == '\n':
				if len(self.tokens) > 0 and self.tokens[-1].type != TokenType.NEWLINE:
					self.add(TokenType.NEWLINE, None)
					while self.c == '\n':
						self.line += 1
						self.advance()
			if self.c <= ' ':
				self.advance()
				continue
			# name
			elif (self.c >= 'a' and self.c <= 'z') or (self.c >= 'A' and self.c <= 'Z') or self.c in'_$@':
				name = self.c
				while self.has_next():
					if (self.next >= 'a' and self.next <= 'z') or (self.next >= 'A' and self.next <= 'Z') or (self.next >= '0' and self.next <= '9') or self.next in'_':
						name += self.next
						self.advance()
					else:
						break
				self.add(TokenType.NAME, name)
			# number
			elif self.c >= '0' and self.c <= '9':
				num = self.c
				while self.has_next():
					if self.next == '_':
						self.advance()
						continue
					elif self.next < '0' or self.next > '9':
						break
					self.advance()
					num += self.c
				# TODO float, convert ...
				self.add(TokenType.NUMBER, num)
			# string
			elif self.c == '\'' or self.c == '"' or self.c == '`':
				string = ''
				quo = self.c
				while self.has_next():
					self.advance()
					if self.c < ' ' and self.c != '\t' and quo != '`':
						raise Exception('Unterminated string.')
					if self.c == quo:
						break
					if self.c == '\\':
						if not self.has_next():
							raise Exception('Unterminated string.')
						self.advance()
						if self.c in ESC_CHAR:
							string += ESC_CHAR[self.c]
					string += self.c
				self.add(TokenType.STRING, string)
			# single line comment
			elif self.c == '/' and self.has_next() and self.next == '/':
				while self.has_next():
					self.advance()
					if self.c == '\n' or self.c == '\r' or not self.has_next():
						self.line += 1
						break
			# single char operators
			elif self.c in '+-*/%!(){},':
				self.add(TokenType.OPERATOR, self.c)
			else:
				print('Ignored: ', self.c)
			self.advance()
		self.add(TokenType.EOF, None)
		for token in self.tokens:
			print(token)

def main():
	lexer = Lexer()
	lexer.tokenize(
r'''17/
fn f(a, b) {
	print(a + b)
}
// comments
2213-3+"ab\ncd"//123'''
)

if __name__ == '__main__':
	main()
