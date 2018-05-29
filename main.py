import json
import sys
import lst

class Tag:
	VAR = 'variable'
	VAR_DEF = 'var_definition'
	FUNC_DEF = 'function_definition'
	ASSIGN = 'assignment'
	APPLY = 'application'
	IF = 'if'
	WHILE = 'while'
	SWITCH = 'switch'
	FOR = 'for'
	BREAK = 'break'
	CONTINUE = 'continue'
	FALLTHROUGH = 'fallthrough'
	RETURN = 'return'

class FunctionType:
	FUNCTION = 'function'
	PRIMITIVE = 'primitive'

	VALUES = [v for k, v in locals().items() if not k.startswith('_')]

class EvalExeption(Exception):
	pass

primitive_const = {
	'null': None,
	'undefined': None,
	'true': True,
	'false': False,
}

## OS
def _output(*xs):
	for x in xs:
		if lst.is_lst(x):
			print(lst.lst2arr(x))
		else:
			print(x, end='')
	print()

def _string_to_char_list(s):
	return lst.lst(*list(s))

def _throw(msg):
	raise EvalExeption(msg)
## PRIMITIVE FUNC

def plus(x, y):
	if isinstance(x, str) and isinstance(y, str):
		return x + y
	elif isinstance(x, str) or isinstance(y, str):
		return str(x) + str(y)
	else:
		return x + y

primitive_func = {
	'$list': lst.lst,
	'$string_to_char_list': _string_to_char_list,
	'$char_code': ord,

	'_-': lambda x: -x,
	'+': plus,
	'-': lambda x, y: x - y,
	'*': lambda x, y: x * y,
	'/': lambda x, y: x // y,
	'/.': lambda x, y: x / y,
	'%': lambda x, y: x % y,
	'**': lambda x, y: x ** y,

	'==': lambda x, y: x == y,
	'!=': lambda x, y: x != y,
	'>': lambda x, y: x > y,
	'>=': lambda x, y: x >= y,
	'<': lambda x, y: x < y,
	'<=': lambda x, y: x <= y,
	'_!': lambda x: not x,
	'&&': lambda x, y: x and y,
	'||': lambda x, y: x or y,

	',': lambda x, y: [x, y],

	'int': lambda x: int(x),
	'round': lambda v, n: round(v, n),

	'input': input,
	'print': _output,
	'throw': _throw,
}

## ENVIRONMENT
def init_env():
	env = ((), {})
	for key, item in primitive_const.items():
		env[1][key] = item
	for key, item in primitive_func.items():
		env[1][key] = (FunctionType.PRIMITIVE, item)
	return env

def add_frame(env):
	return (env, {})

def make_frame(vars, vals):
	if len(vars) != len(vals):
		raise EvalExeption('error, make frames')
	frame = {}
	for i in range(0, len(vars)):
		frame[vars[i]] = vals[i]
	return frame

def extend_env(env, vars, vals):
	return (env, make_frame(vars, vals))

def loopup_var(stmt, var, env):
	def env_loop(env):
		if len(env) == 0:
			raise EvalExeption("Cannot find variable: " + var)
		elif var in env[1]:
			return env[1][var]
		else:
			return env_loop(env[0])
	return env_loop(env)

def set_var_val(stmt, var, val, env):
	def env_loop(env):
		if len(env) == 0:
			raise EvalExeption("Cannot find variable: " + var)
			return False
		elif var in env[1]:
			env[1][var] = val
			return True
		else:
			env_loop(env[0])
	return env_loop(env)

def add_var_val(stmt, var, val, env):
	env[1][var] = val

## UTIL
def is_tagged_value(val, tag):
	return isinstance(val, dict) and val.get('tag') == tag

def is_self_evaluating(stmt):
	return stmt == [] or isinstance(stmt, (int, float)) or isinstance(stmt, str)

def apply_primitive_func(fun, args):
	return fun(*args)

def is_func_tuple(x):
	return isinstance(x, tuple) and len(x) > 1 and x[0] in FunctionType.VALUES

def list_of_values(lst, env):
	return list(map(lambda v: evaluate(v, env), lst))

## STATEMENT EVALUATION

def eval_sequence(stmt, env):
	for s in stmt:
		val = evaluate(s, env)
		if is_tagged_value(val, 'return_value'):
			return val
	return None

def eval_var_def(stmt, env):
	var_value = evaluate(stmt['right'], env)
	add_var_val(stmt, stmt['left'], var_value, env)
	return var_value

def eval_func_def(stmt, env):
	return (FunctionType.FUNCTION, {
			'tag': 'function_value',
			'name': stmt['name'],
			'parameters': stmt['parameters'],
			'body': stmt['body'],
			'env': env,
		})

def eval_assign(stmt, env):
	val = evaluate(stmt['right'], env)
	left_val = evaluate(stmt['left'], env) if stmt['returnLeft'] else None
	# TODO func ref, array indexing
	if is_tagged_value(stmt['left'], Tag.APPLY):
		# TODO array indexing
		fun, member = stmt['left']['operands']
		set_var_val(stmt, member['name'], val, evaluate(fun, env)[1]['env'])
	else:
		set_var_val(stmt, stmt['left']['name'], val, env)
	return left_val if stmt['returnLeft'] else val

def eval_if_stmt(stmt, env):
	if evaluate(stmt['predicate'], env):
		return evaluate(stmt['consequent'], extend_env(env, [], []))
	elif stmt.get('alternative'):
		return evaluate(stmt['alternative'], extend_env(env, [], []))

def eval_switch_stmt(stmt, env):
	found_case = False
	for case in stmt['cases']:
		if found_case:
			break
		result = None
		if evaluate(stmt['variable'], env) in case['value']:
			found_case = True
			result = evaluate(case['stmt'], extend_env(env, [], []))
		if is_tagged_value(result, 'return_value'):
			return result
		elif is_tagged_value(result, 'break_value'):
			return None
		elif is_tagged_value(result, 'fallthrough_value'):
			found_case = False
	if not found_case and stmt['default']:
		return evaluate(stmt['default'], extend_env(env, [], []))

def eval_while_stmt(stmt, env):
	if evaluate(stmt['predicate'], env):
		result = evaluate(stmt['consequent'], extend_env(env, [], []))
		if is_tagged_value(result, 'return_value'):
			return result
		if is_tagged_value(result, 'break_value'):
			return None
		return eval_while_stmt(stmt, env)

def eval_for_stmt(stmt, env):
	for_range = stmt['range']
	for_env = extend_env(env, [], [])
	for_var = stmt['variable']
	if is_tagged_value(for_range, 'range'):
		# value range
		range_from_val = evaluate(for_range['from'], env)
		add_var_val(None, for_var['name'], range_from_val, for_env)
		return eval_for_range(stmt, 
			evaluate(for_range['to']),
			range['closed'],
			evaluate(stmt['increment'] or 1, env),
			for_env)
	elif is_tagged_value(for_range, 'variable') or is_tagged_value(for_range, 'application'):
		range_val = evaluate(for_range, env)
		add_var_val(stmt, for_var['name'], None, for_env)
		if lst.is_lst(range_val):
			return eval_for_lst(stmt, range_val, for_env)
		else:
			raise EvalExeption('Unsupported for range')
	else:
		raise EvalExeption('Unsupported for range')

def eval_for_range(stmt, range_to_val, range_closed, increment, env):
	var_val = evaluate(stmt['variable'], env)
	if (increment > 0 and (
			(not range_closed and var_val < range_to_val) or (range_closed and var_val <= range_to_val)
		)) or (increment < 0 and (
			(not range_closed and var_val > range_to_val) or (range_closed and var_val >= range_to_val)
		)):
		result = evaluate(stmt['consequent'], env)
		if is_tagged_value(result, 'return_value'):
			return result
		elif is_tagged_value(result, 'break_value'):
			return None
		set_var_val(stmt, stmt['variable']['name'], var_val+increment, env)
		return eval_for_range(stmt, range_to_val, range_closed, increment, env)

def eval_for_lst(stmt, range_lst, env):
	if (lst.is_empty(range_lst)):
		return None
	set_var_val(stmt, stmt['variable']['name'], lst.head(range_lst), env)
	result = evaluate(stmt['consequent'], env)
	if is_tagged_value(result, 'return_value'):
		return result
	elif is_tagged_value(result, 'break_value'):
		return None
	return eval_for_lst(stmt, lst.tail(range_lst), env)

def eval_return(stmt, env):
	return {
		'tag': 'return_value',
		'content': evaluate(stmt['expression'], env),
	}

def eval_apply(fun, args, env):
	if fun[0] == FunctionType.PRIMITIVE:
		return apply_primitive_func(fun[1], args)
	elif fun[0] == FunctionType.FUNCTION:
		func = fun[1]
		func_env = extend_env(func['env'], func['parameters'], args)
		result = evaluate(func['body'], func_env)
		if is_tagged_value(result, 'return_value'):
			return result['content']
		return None
	else:
		raise EvalExeption('Unknown application')

def eval_logic(fun_raw, args, env):
	fun_name = fun_raw['name']
	operand_1 = evaluate(args[0], env)
	operand_2 = None
	if (fun_name == '&&' and operand_1 == True) or (fun_name == '||' and operand_1 == False):
		operand_2 = evaluate(args[1], env)
	fun = evaluate(fun_raw, env)
	arg_list = [operand_1, operand_2]
	return apply_primitive_func(fun[1], arg_list)

def eval_refer(fun, member, env):
	if is_func_tuple(fun):
		func = fun[1]
		func_env = extend_env(func['env'], [], [])
		if func['body']:
			evaluate(func['body'], func_env)
		return loopup_var(None, member, func_env)
	if lst.is_lst(fun) or lst.is_pair(fun):
		return lst_method(fun, member)
	raise EvalExeption('Unknown reference')

## DS
def lst_method(xs, method):
	if method == 'head':
		return lst.head(xs)
	elif method == 'tail':
		return lst.tail(xs)
	elif method == 'isEmpty':
		return lst.is_empty(xs)
	else:
		raise EvalExeption('Unknown list method')


## EVALUATE

def evaluate(stmt, env):
	if isinstance(stmt, dict):
		#print('EVAL ' + str(stmt.get('tag')) + ' ' + str(stmt.get('name')))
		#print(stmt.get('line'))
		pass
	if isinstance(stmt, list):
		return eval_sequence(stmt, env)
	elif is_self_evaluating(stmt):
		return stmt
	elif is_tagged_value(stmt, Tag.VAR):
		# variable
		return loopup_var(stmt, stmt['name'], env)
	elif is_tagged_value(stmt, Tag.VAR_DEF):
		# variable definition
		return eval_var_def(stmt, env)
	elif is_tagged_value(stmt, Tag.FUNC_DEF):
		# function definition
		return eval_func_def(stmt, env)
	elif is_tagged_value(stmt, Tag.ASSIGN):
		# assignment
		return eval_assign(stmt, env)
	elif is_tagged_value(stmt, Tag.IF):
		# if
		return eval_if_stmt(stmt, env)
	elif is_tagged_value(stmt, Tag.SWITCH):
		# switch
		return eval_switch_stmt(stmt, env)
	elif is_tagged_value(stmt, Tag.WHILE):
		# while
		return eval_while_stmt(stmt, env)
	elif is_tagged_value(stmt, Tag.FOR):
		# for
		return eval_for_stmt(stmt, env)
	elif is_tagged_value(stmt, Tag.APPLY):
		# application
		operator = stmt['operator']
		operands = stmt['operands']
		if operator['name'] == '&&' or operator['name'] == '||':
			return eval_logic(operator, operands, env)
		elif operator['name'] == '.':
			# reference
			fun, member = operands
			if is_tagged_value(member, Tag.APPLY):
				member_func_name = member['operator']['name']
				return eval_apply(eval_refer(evaluate(fun, env), member_func_name, env), list_of_values(member['operands'], env), env)
			else:
				return eval_refer(evaluate(fun, env), member['name'], env)
		return eval_apply(evaluate(operator, env), list_of_values(operands, env), env)
	elif is_tagged_value(stmt, Tag.BREAK):
		# break
		return {'tag': 'break_value'}
	elif is_tagged_value(stmt, Tag.CONTINUE):
		# continue
		return {'tag': 'continue_value'}
	elif is_tagged_value(stmt, Tag.FALLTHROUGH):
		# fallthrough
		return {'tag': 'fallthrough_value'}
	elif is_tagged_value(stmt, Tag.RETURN):
		# return
		return eval_return(stmt, env)
	else:
		raise EvalExeption('Unsupported statement')

def main(ast_str):
	try:
		ast = json.loads(ast_str)
		evaluate(ast, init_env())
	except EvalExeption as e:
		print('[ERROR]' + str(e))
	except KeyboardInterrupt:
		print('\nInterrupted')

if __name__ == '__main__':
	file_name = 'ast.json'
	if len(sys.argv) > 1:
		file_name = sys.argv[1]
	with open(file_name) as f:
		source = f.read()
		main(source)
