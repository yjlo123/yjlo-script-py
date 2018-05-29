def lst(*args):
	lst = []
	for arg in reversed(args):
		lst = [arg, lst]
	return lst

def lst2arr(xs):
	result = []
	while not is_empty(xs):
		result.append(head(xs))
		xs = tail(xs)
	return result

def is_empty(xs):
	return xs == []

def head(xs):
	return xs[0]

def tail(xs):
	return xs[1]

def is_lst(xs):
	if xs == []:
		return True
	elif is_pair(xs):
		return is_lst(tail(xs))
	return False

def pair(x, xs):
	return [x, xs]

def is_pair(xs):
	return isinstance(xs, list) and len(xs) == 2

if __name__ == "__main__":
	pass
