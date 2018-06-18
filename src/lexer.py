from enum import Enum

class TokenType(Enum):
	NEWLINE = 'newline'
	EOF = 'eof'
	NAME = 'name'
	NUMBER = 'number'
	STRING = 'string'
	OPERATOR = 'operator'

class Token(object):
	def __init__(self, t, value=None, line=-1):
		self.type = t
		self.value = value
		self.line = line

	def __str__(self):
		return '[{0}] {1}	{2}'.format(self.line, self.type.name, [self.value])

class Lexer(object):
	ESC_CHAR = {
		'b': '\b',
		'f': '\f',
		'n': '\n',
		'r': '\r',
		't': '\t',
	}

	OPERATORS = {
		'+': ['=', '+'],
		'-': ['=', '-'],
		'*': ['=', '*'],
		'/': ['=', '.'],
		'%': ['='],
		':': ['='],
		'=': ['=', '=='],
		'>': ['=', '>', '>>'],
		'<': ['=', '<'],
		'!': ['='],
		'^': ['='],
		'&': ['=', '&'],
		'|': ['=', '|'],
		'.': ['.', '..', '.<', '.>'],
	}

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
				self.next = self.s[self.i + 1]
			else:
				self.next = None
		else:
			self.c = self.next
			self.next = None

	def has_next(self):
		return self.i + 1 < self.len

	def peek_next(self, n=1):
		if self.i + n < self.len:
			return self.s[self.i + n]
		return None

	def make_name(self):
		name = self.c
		while self.has_next():
			if self._is_letter(self.next) or self._is_digit(self.next) or self.next in'_':
				name += self.next
				self.advance()
			else:
				break
		self.add(TokenType.NAME, name)

	def make_number(self):
		num = self.c
		while self.has_next():
			if self.next == '_':
				self.advance()
				continue
			elif not self._is_digit(self.next):
				break
			self.advance()
			num += self.c
		if self.has_next() and self.next == '.' and self._is_digit(self.peek_next(2)):
			self.advance()
			num += self.c
			while self.has_next():
				if self.next == '_':
					self.advance()
					continue
				elif not self._is_digit(self.next):
					break
				self.advance()
				num += self.c
		num = float(num) if '.' in num else int(num)
		self.add(TokenType.NUMBER, num)

	def make_string(self):
		string = ''
		quo = self.c
		while self.has_next():
			self.advance()
			if self.c < ' ' and self.c != '\t' and quo != '`':
				raise Exception('[Lexer] Unterminated string.')
			if self.c == quo:
				break
			if self.c == '\\':
				if not self.has_next():
					raise Exception('[Lexer] Unterminated string.')
				self.advance()
				if self.c in self.ESC_CHAR:
					string += self.ESC_CHAR[self.c]
			string += self.c
		self.add(TokenType.STRING, string)

	def make_operator(self):
		prefix = self.c
		suffix_candidates = self.OPERATORS[prefix]
		suffix = ''
		while self.has_next() and suffix + self.next in suffix_candidates:
			suffix += self.next
			self.advance()
		self.add(TokenType.OPERATOR, prefix + suffix)

	def make_comment(self):
		self.advance()
		# block comment
		if self.c == '*':
			while self.has_next():
				self.advance()
				if self.c == '\n':
					self.line += 1
				elif self.c == '*' and self.has_next() and self.next == '/':
					self.advance()
					break
		# single line comment
		elif self.c == '/':
			while self.has_next():
				self.advance()
				if self.c == '\n' or self.c == '\r' or not self.has_next():
					self.line += 1
					break
		else:
			# should never reach here
			raise Exception('[Lexer] Lexing error')

	@staticmethod
	def _is_digit(char):
		return char >= '0' and char <= '9'

	@staticmethod
	def _is_letter(char):
		return (char >= 'a' and char <= 'z') or (char >= 'A' and char <= 'Z')

	def tokenize(self, source):
		self.init_source(source)
		self.advance()
		while self.c is not None:
			# new line
			if self.c == '\n':
				# keep only one new-line as a token
				if len(self.tokens) > 0 and self.tokens[-1].type != TokenType.NEWLINE:
					self.add(TokenType.NEWLINE, None)
				while self.c == '\n':
					self.line += 1
					self.advance()
			# ignore spaces
			if self.c <= ' ':
				self.advance()
				continue
			# name
			elif self._is_letter(self.c) or self.c in'_$@':
				self.make_name()
			# number
			elif self._is_digit(self.c):
				self.make_number()
			# string
			elif self.c == '\'' or self.c == '"' or self.c == '`':
				self.make_string()
			# comment
			elif self.c == '/' and self.has_next() and self.next in '*/':
				self.make_comment()
			# operators
			elif self.c in self.OPERATORS:
				self.make_operator()
			# single char operators
			else:
				self.add(TokenType.OPERATOR, self.c)
			# move to next token
			self.advance()
		self.add(TokenType.EOF, None)
		return self.tokens

def main():
	lexer = Lexer()
	tokens = lexer.tokenize(
r'''17/
/* a
This is a block comment
*/
fn f(a, b) {
	print(a * b++)
}
// comments
2213-3.56+"ab\ncd";alert()//123
_a''')
	for token in tokens:
		print(token)

if __name__ == '__main__':
	main()
