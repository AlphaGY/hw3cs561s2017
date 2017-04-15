# category P = 1 EU = 2 MEU = 3
# variable dict = query variables
# evidence dict = evidence variables
class Query:
    category = 0
    variable = {}
    evidence = {}

    def __init__(self, cate, vars, evds):
        self.category = cate
        self.variable = vars
        self.evidence = evds
        pass


# category chance = 1 decision = 2 utility = 3
# name = node's name
# parent list = parents' names
# probability dict = probability of truth of different distributions over parents' nodes
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


# read one query from one line
def read_query(q_line):
    # detect query's category
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
        # query variable
        if not evidence_flag:
            # MEU query
            if cate == 3:
                query.variable[q_line[i]] = True
                i += 1
            # P or EU query
            else:
                if q_line[i + 4] == '+':
                    query.variable[q_line[i]] = True
                else:
                    query.variable[q_line[i]] = False
                i += 5
        # evidence variable
        else:
            if q_line[i + 4] == '+':
                query.evidence[q_line[i]] = True
            else:
                query.evidence[q_line[i]] = False
            i += 5
    return query


# read chance node and decision node
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
    # read CPT
    node_line = file.readline()
    node_line = node_line[0:len(node_line) - 1]
    # decision node
    if node_line == 'decision':
        node.category = 2
        node_line = file.readline()
        return node, node_line
    # chance node
    # no parent
    if len(node.parent) == 0:
        node.probability[''] = float(node_line)
        node_line = file.readline()
        return node, node_line
    # has parent
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


# read utility node
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


# calculate the probability for a certain variable given its parents' distribution
def calculate_probability(var, key, flag):
    # decision node
    if var.category == 2:
        return 1
    # chance node
    if flag:
        return var.probability[key]
    else:
        return 1 - var.probability[key]


# check whether variable has been assigned a value given evidence
def in_evidence(var, evidence):
    return evidence.has_key(var.name)


# return the key for the node's parents's distribution given evidence
def parents(var, evidence):
    key = ''
    for p in var.parent:
        if evidence[p]:
            key += '1'
        else:
            key += '0'
    return key


# extend evidence with a single variable e += var:flag
def extend_evidence_single(e, var, flag):
    extd = {}
    keys = e.keys()
    for k in keys:
        extd[k] = e[k]
    extd[var.name] = flag
    return extd


# extend evidence with multi variables e += {vars:key}
def extend_evidence_multi(e, vars, key):
    extd = {}
    keys = e.keys()
    for k in keys:
        extd[k] = e[k]
    keys = vars.keys()
    for i in range(len(keys)):
        if key[i] == '1':
            extd[keys[i]] = True
        else:
            extd[keys[i]] = False
    return extd


# return the remaining set after popping out the first element
def get_rest(vars):
    rest = []
    if len(vars) > 1:
        rest = vars[1:len(vars)]
    return rest


# sum up probability for vars given evidence
def enumerate_all(vars, e):
    if len(vars) == 0:
        return 1.0
    y = vars[0]
    rest = get_rest(vars)
    if in_evidence(y, e):
        return calculate_probability(y, parents(y, e), e[y.name]) * enumerate_all(rest, e)
    else:
        t = calculate_probability(y, parents(y, e), True) * enumerate_all(rest, extend_evidence_single(e, y, True))
        f = calculate_probability(y, parents(y, e), False) * enumerate_all(rest, extend_evidence_single(e, y, False))
        return t + f


# generate keys for possible distributions over n variables
def distributions(number):
    dis = []
    for i in range(2 ** number):
        b = str(bin(i).replace('0b', ''))
        if len(b) < number:
            b = '0' * (number - len(b)) + b
        dis.append(b)
    return dis


# calculate a distribution over query variables
def enumeration_ask(q, e, vars):
    dtrbs = distributions(len(q))
    p = {}
    sum = 0
    for d in dtrbs:
        p[d] = enumerate_all(vars, extend_evidence_multi(e, q, d))
        sum += p[d]
    for d in dtrbs:
        p[d] /= sum
    return p


# probability query
def query_probability(query, vars):
    # calculate the distribution for query variables given evidence
    p = enumeration_ask(query.variable, query.evidence, vars)
    # get specific probability for query variables according to their truth values in the query
    key = ''
    vars = query.variable.keys()
    for v in vars:
        if query.variable[v]:
            key += '1'
        else:
            key += '0'
    return p[key]


# delete impossible distribution
# i, flag indicate that the i-th variable's truth must be the same as flag
# if not then it is impossible and should be deleted
def delete_impossible_distribution(dis, i, flag):
    j = 0
    while j < len(dis):
        if flag and dis[j][i] == '0':
            del dis[j]
        elif not flag and dis[j][i] == '1':
            del dis[j]
        else:
            j += 1
    return dis


# possible distributions for certain variables given evidence
def distributions_specific(vars, evidence):
    dis = distributions(len(vars))
    for i in range(len(vars)):
        if evidence.has_key(vars[i]):
            dis = delete_impossible_distribution(dis, i, evidence[vars[i]])
    return dis


# compute expected utility
def query_eu(query, vars, utility):
    eu = 0
    # new evidence variables for EU = query variables + evidence variables
    known = {}
    for k in query.variable.keys():
        known[k] = query.variable[k]
    for k in query.evidence.keys():
        known[k] = query.evidence[k]
    # parents of the utility node excluding those in the evidence are the new query variables
    # possible distributions
    dis = distributions_specific(utility.parent, known)
    for d in dis:
        prnts = {}
        for i in range(len(d)):
            if not known.has_key(utility.parent[i]):
                if d[i] == '1':
                    prnts[utility.parent[i]] = True
                else:
                    prnts[utility.parent[i]] = False
        prb_query = Query(1, prnts, known)
        prb = query_probability(prb_query, vars)
        u = utility.probability[d]
        eu += (prb * u)
    return int(round(eu))


# compute max expected utility
def query_meu(query, vars, utility):
    # compute EU for all possible distributions over query variables
    dis = distributions(len(query.variable))
    keys = query.variable.keys()
    max = -10000
    best = ''
    for d in dis:
        q_vars = {}
        for i in range(len(d)):
            if d[i] == '1':
                q_vars[keys[i]] = True
            else:
                q_vars[keys[i]] = False
        eu_query = Query(2, q_vars, query.evidence)
        eu = query_eu(eu_query, vars, utility)
        if eu > max:
            max = eu
            best = d
    return max, best

# execute query
def do_query(query, vars, utility):
    # P query
    if query.category == 1:
        return "%.2f" % query_probability(query, vars)
    # EU query
    elif query.category == 2:
        return str(query_eu(query, vars, utility))
    # MEU query
    else:
        max, best = query_meu(query, vars, utility)
        best_str = ''
        for i in range(len(best)):
            if best[i] == '1':
                best_str += '+ '
            else:
                best_str += '- '
        best_str += str(max)
        return best_str


# read file
infile = open("input.txt", "r")
line = infile.readline()
queries = []
nodes = []
utility = Node(3, 'utility', {}, {})
result = []
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
        queries.append(q)
    elif flag == 2:
        node, line = read_node(line, infile)
        nodes.append(node)
        continue
    elif flag == 3:
        utility, line = read_utility(line, infile)
        continue
    line = infile.readline()
result = ''
for q in queries:
    result += do_query(q, nodes, utility) + '\n'
# write file
outfile = open('output.txt', 'w')
outfile.write(result)
