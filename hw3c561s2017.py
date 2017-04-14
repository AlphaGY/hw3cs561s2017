import null


# category P=1 EU=2 MEU=3
class Query:
    category = 0
    variable = {}
    evidence = {}

    def __init__(self, cate, vars, evds):
        self.category = cate
        self.variable = vars
        self.evidence = evds
        pass


# category chance=1 decision=2 utility=3
class Node:
    category = 0
    name = ''
    parent = []
    probability = {}

    def __init__(self, cate, n, prnt, prb):
        self.category = cate
        self.name = n
        self.parent = prnt
        self.probability = prb
        pass


def print_query(q):
    if q.category == 1:
        print 'P'
    elif q.category == 2:
        print 'EU'
    else:
        print 'MEU'
    print q.variable
    print '|'
    print q.evidence


def print_node(n):
    if n.category == 1:
        print 'chance'
    elif n.category == 2:
        print 'decision'
    else:
        print 'utility'
    print n.name
    print n.parent
    print n.probability


# read one query from one line
def read_query(q_line):
    if q_line[0] == 'P':
        cate = 1
        query = Query(cate, {}, {})
        i = 2
    elif q_line[0] == 'E':
        cate = 2
        query = Query(cate, {}, {})
        i = 3
    else:
        cate = 3
        query = Query(cate, {}, {})
        i = 4
    # flag True=variable False=evidence
    evidence_flag = False
    while q_line[i] != ')':
        if q_line[i] == ',':
            i += 2
        elif q_line[i] == ' ':
            evidence_flag = True
            i += 3
        if not evidence_flag:
            # MEU query
            if cate == 3:
                query.variable[q_line[i]] = True
                i += 1
            else:
                if q_line[i + 4] == '+':
                    query.variable[q_line[i]] = True
                else:
                    query.variable[q_line[i]] = False
                i += 5
        else:
            if q_line[i + 4] == '+':
                query.evidence[q_line[i]] = True
            else:
                query.evidence[q_line[i]] = False
            i += 5

    return query


def read_node(node_line, file):
    name = node_line[0]
    # no parent
    if node_line[1] == '\n':
        node = Node(1, name, [], {})
    # has parents
    else:
        prnt = []
        i = 4
        while True:
            prnt.append(node_line[i])
            if node_line[i + 1] == '\n':
                break
            i += 2
        node = Node(1, name, prnt, {})

    node_line = file.readline()
    node_line = node_line[0:len(node_line) - 1]
    # decision node
    if node_line == 'decision':
        node.category = 2
        node_line = file.readline()
        return node, node_line
    # no parent
    if len(node.parent) == 0:
        node.probability[''] = float(node_line)
        node_line = file.readline()
        return node, node_line
    while len(node_line) != 0 and node_line[0] != '*':
        splits = node_line.split(' ')
        key = ''
        for i in range(1, len(node.parent) + 1):
            if splits[i] == '+' or splits[i] == '+\n':
                key += '1'
            else:
                key += '0'
        node.probability[key] = float(splits[0])
        node_line = file.readline()
    return node, node_line


def read_utility(utility_line, file):
    prnt = []
    i = 10
    while True:
        prnt.append(utility_line[i])
        if utility_line[i + 1] == '\n':
            break
        i += 2
    node = Node(3, 'utility', prnt, {})
    utility_line = file.readline()
    while len(utility_line) != 0:
        splits = utility_line.split(' ')
        key = ''
        for i in range(1, len(node.parent) + 1):
            if splits[i] == '+' or splits[i] == '+\n':
                key += '1'
            else:
                key += '0'
        node.probability[key] = float(splits[0])
        utility_line = file.readline()
    return node, utility_line


# read file
infile = open("input.txt", "r")
line = infile.readline()
queries = []
nodes = []
utility = null
# file location flag 1=queries 2=chance nodes & decision nodes 3=utility node
flag = 1
while line != '':
    if line == '******\n' and flag == 1:
        flag = 2
        line = infile.readline()
    if line == '******\n' and flag == 2:
        flag = 3
        line = infile.readline()
    if line == '***\n':
        line = infile.readline()
    if flag == 1:
        q = read_query(line)
        print_query(q)
        queries.append(q)
    elif flag == 2:
        node, line = read_node(line, infile)
        print_node(node)
        nodes.append(node)
        continue
    elif flag == 3:
        utility, line = read_utility(line, infile)
        print_node(utility)
        continue
    line = infile.readline()
