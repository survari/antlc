import re
from functools import reduce
from sys import argv

symbols = []

def lexer(string):
	string = re.sub(r'(\s|^)/.*\n','',string+'\n')
	stringlit = r'"[^"]*"'
	num = r'\-?\d*\.?\d+'
	frac = num + r'/' + num
	word = r'[A-Za-z\-_]+[A-Za-z0-9\-_]*'
	operator = r'\S̶|\S'
	regex = [stringlit, frac, word, num, operator]
	tokens = re.findall('|'.join(regex), string)
	result = []
	for token in tokens:
		if bool(re.match('^('+num+'|'+frac+')$', token)):
			result.append(('num',eval(token)))
		elif token.startswith('"'):
			result.append(('str',token[1:-1].replace('\n',' ')))
		elif token in ['(',')','{','}','/',':',';']:
			result.append(('special',token))
		elif bool(re.match('^'+word+'$', token)):
			result.append(('rcl',token))
		else:
			result.append(('prm',token))
	return result

def index_of_close(tokens):
	nesting = 1
	index = 1
	groups = [[]]
	for token in tokens[1:]:
		if token == ('special', '(') or token == ('special', '{'): nesting += 1
		if token == ('special', ')') or token == ('special', '}'): nesting -= 1
		if (token == ('special', ')') or token == ('special', '}')) and nesting == 0:
			return {'index': index, 'groups': groups}
		if token == ('special', ';') and nesting == 1: groups.append([])
		else: groups[-1].append(token)
		index += 1
	return {'index': index, 'groups': groups}

def parser(tokens):
	if len(tokens) == 0:
		return []
	if len(tokens) == 1 and len(tokens[0]) == 2 and tokens[0][0] in ['num','str','rcl','prm']:
		return [tokens[0]]
	if len(tokens) > 1 and tokens[0] == ('special','(') and tokens[1] == ('special',')'):
		return parser([['nil']]+tokens[2:])
	if len(tokens) > 2 and tokens[0] == ('special','('):
		i = index_of_close(tokens)['index']
		return parser([parser(tokens[1:i])]+tokens[1+i:])
	if len(tokens) > 2 and tokens[0] == ('special', '{'):
		o = index_of_close(tokens)
		inner = reduce(lambda l1,l2: l1+['cls']+l2,list(map(parser, o['groups'])))
		outer = tokens[1+o['index']:]
		return parser([[('fun',len(inner))]+inner] + outer)
	if len(tokens) > 1 and tokens[1] == ('special','/'):
		return parser([parser([tokens[0]])+['rdc']]+tokens[2:])
	if len(tokens) > 3 and tokens[1] == ('special','('):
		i = index_of_close(tokens[1:])['index']
		return parser([tokens[0],parser(tokens[2:i+1])]+tokens[2+i:])
	if len(tokens) > 3 and tokens[1] == ('special','{'):
		o = index_of_close(tokens[1:])
		return parser([tokens[0],[tokens[1]]+list(map(parser, o['groups']))]+tokens[2+o['index']:])
	if len(tokens) > 2 and tokens[2] == ('special','/'):
		return parser([tokens[0],parser([tokens[1]]) + ['rdc']]+tokens[3:])
	if len(tokens) > 2 and tokens[1] == ('special', ':') and tokens[0][0] == 'rcl':
		return parser(tokens[2:]) + [('sto', tokens[0][1])]
	if len(tokens) > 2:
		return parser([tokens[1]]) + parser([tokens[0]]) + parser(tokens[2:]) + [('app', 2)]
	if len(tokens) == 1 and isinstance(tokens[0], list):
		return tokens[0]
	if len(tokens) == 1:
		raise Exception('Unexpected ' + str(tokens[0][1]))
	else:
		raise Exception('Syntax Error')

def generate(cmds):
	if cmds == []: return ''
	res = ''
	for cmd in cmds:
		if isinstance(cmd, tuple) and len(cmd) == 2:
			res += cmd[0] + str(cmd[1]) + '\n'
		else:
			res += cmd + '\n'
	res += 'dsp'
	return res

compiler = lambda string: generate(parser(lexer(string)))

if __name__ == '__main__':
	if len(argv) == 1:
		while True:
			try:
				string = input('[DEBUG] ')
				tokens = lexer(string)
				cmds = parser(tokens)
				asm = generate(cmds)
				print(asm)
			except Exception as e:
				print(e)
	else:
		for filename in argv[1:]:
			antfile = open(filename)
			lines = antfile.read().split("\n")
			antfile.close()
			asm = ''
			for line in lines:
				result = compiler(line)
				if result != '':
					asm += result + '\n'
			asmfile = open(filename+'.asm', 'w')
			asmfile.write(asm)
			asmfile.close()
