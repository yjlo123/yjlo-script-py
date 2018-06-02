
class TokenType():
	NEWLINE = 'newline'
	NAME = 'name'
	NUMBER = 'number'
	STRING = 'string'
	OPERATOR = 'operator'

def make(t, v, l):
	return {
		'type': t,
		'value': v,
		'line': l,
	}

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
			if len(tokens) > 0:
				tokens.append(make(TokenType.NEWLINE, None, line))
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
			tokens.append(make(TokenType.NUMBER, num, line))
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
			tokens.append(make(TokenType.STRING, string, line))
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
			tokens.append(make(TokenType.OPERATOR, c, line))
		else:
			print('Ignored: ', c)
		i += 1
	for token in tokens:
		print(token)

def main():
	tokenize(
r'''17/

// comments
2213-3+"ab\ncd"//123'''
)

if __name__ == '__main__':
	main()
