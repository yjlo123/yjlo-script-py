
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
		return '[{0}]	{1}'.format(self.type, str(self.value))

ESC_CHAR = {
	'b': '\b',
	'f': '\f',
	'n': '\n',
	'r': '\r',
	't': '\t',
}

def tokenize(s):
	tokens = []
	line = 1
	i = 0
	length = len(s)
	while i < length:
		c = s[i]
		# new line
		if c == '\n':
			if len(tokens) > 0 and tokens[-1].type != TokenType.NEWLINE:
				tokens.append(Token(TokenType.NEWLINE, None, line))
				while c == '\n':
					line += 1
					i += 1
					c = s[i]
		# number
		if c <= ' ':
			i += 1
			continue
		elif c >= '0' and c <= '9':
			num = c
			while i + 1 < length:
				c = s[i+1]
				if c == '_':
					i += 1
					c = s[i]
					continue
				elif c < '0' or c > '9':
					break
				i += 1
				num += c
			# TODO float, convert ...
			tokens.append(Token(TokenType.NUMBER, num, line))
		# string
		elif c == '\'' or c == '"' or c == '`':
			string = ''
			quo = c
			i += 1
			while i < length:
				c = s[i]
				if c < ' ' and c != '\t' and quo != '`':
					raise Exception('Unterminated string.')
				if c == quo:
					break
				if c == '\\':
					i += 1
					if i >= length:
						raise Exception('Unterminated string.')
					c = s[i]
					if c in ESC_CHAR:
						c = ESC_CHAR[c]
				string += c
				i += 1
			tokens.append(Token(TokenType.STRING, string, line))
		# single line comment
		elif c == '/' and i+1 < length and s[i+1] == '/':
			i += 1
			while i < length:
				c = s[i]
				if c == '\n' or c == '\r' or i == length:
					line += 1
					break
				i += 1
		# single char operators
		elif c in '+-*/%!':
			tokens.append(Token(TokenType.OPERATOR, c, line))
		else:
			print('Ignored: ', c)
		i += 1
	tokens.append(Token(TokenType.EOF, None, line))
	for token in tokens:
		print(token)

def main():
	tokenize(
r'''17/
fn f(a, b) {
	print(a + b)
}
// comments
2213-3+"ab\ncd"//123'''
)

if __name__ == '__main__':
	main()
