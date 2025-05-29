import random, string, ast, base64, builtins, sys, hashlib

possible_returns = "True False 0 1 2 3 4 5 '' \"\"".split(" ")
used_vars = set()
rename_dict = {}

def random_name(length=10):
    return random.choice(string.ascii_letters) + "".join(random.choices(string.ascii_letters + string.digits, k=length - 1))

def random_var(length=10):
    rdm_var = random_name(length)
    while rdm_var in used_vars:
        rdm_var = random_name(length)
    used_vars.add(rdm_var)
    return rdm_var

def random_var_len():
    return random_var(random.randint(40, 60))

def init_vars(script):
    tree = ast.parse(script)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used_vars.add(node.id)

def add_randcode(script):
    for i in range(random.randint(40, 60)):
        func_name = random_var_len()
        params = list(random_var_len() for _ in range(random.randint(3, 7)))
        new_code = f"""
def {func_name}({','.join(params)}):
    if {random.choice(params)}=={random.choice(params)}:
        return {random.choice(possible_returns)}
{"\n".join(f"""    elif {random.choice(params)}=={random.choice(params)}:
        return {random.choice(possible_returns)}""" for _ in range(random.randint(2, 4)))}
    raise Exception('{random_var_len()}')
"""
        if i % 2 == 0:
            script += new_code
        else:
            script = new_code + script
    return script

def encode_decode(script):
    b85 = base64.b85encode(script.encode("utf-8"))
    code_name = random_var_len()
    return f"""{code_name} = {b85}
import base64
exec(base64.b85decode({code_name}).decode('utf-8'))
"""

class NameVisitor(ast.NodeTransformer):
    def visit_Name(self, node):
        if "parent" in vars(node):
            node.id = rename_dict[node.id]
        return node

def randomize_name(script, pkg):
    init_code = ""
    tree = ast.parse(script)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            for child in ast.iter_child_nodes(node):
                child.parent = node
        elif isinstance(node, ast.Name):
            if node.id not in rename_dict:
                rename_dict[node.id] = random_var_len()
                if node.id in vars(builtins) or node.id in pkg:
                    init_code += f"{rename_dict[node.id]}={node.id}\n"
    visitor = NameVisitor()
    tree = visitor.visit(tree)
    return init_code + ast.unparse(tree)

def modify_protection1(script):
    return script + f"""
import sys
try:
    {'\n    '.join(used_vars)}
except:
    print('CAUGHT!')
    sys.exit()
"""

def modify_protection2(script):
    hash = hashlib.sha3_512("".join(used_vars).encode("utf-8")).hexdigest()
    length = len(used_vars)
    chunk_count = length // 5
    secret_chunks = [hash[i * 5:i * 5+5] for i in range(chunk_count)]
    secret_names = [random_var_len() for _ in range(chunk_count)]
    for i in range(chunk_count):
        script += f"""
{secret_names[i]} = '{secret_chunks[i]}'
"""
    script += f"""
if {'+'.join(secret_names)} != '{hash}':
    print('CAUGHT!')
    sys.exit()
"""
    return script

def top_imports(script):
    init_code = ""
    tree = ast.parse(script)
    for node in ast.walk(tree):
        # bundle.py 참고해서 작성함
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    init_code += f"import {alias.name} as {alias.asname}\n"
                else:
                    init_code += f"import {alias.name}\n"
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports = set()
            for alias in node.names:
                imports.add(alias.name)
            init_code += f"from {module} import {','.join(imports)}\n"
    return init_code + script    

def obfuscate(script, pkg):
    print("Intializing")
    init_vars(script)
    print("Adding random codes")
    script = add_randcode(script)
    print("Randomizing names")
    script = randomize_name(script, pkg)
    print("Protection from modification")
    script = modify_protection1(script)
    print("Protection from modification")
    script = modify_protection2(script)
    print("Imports at the top")
    script = top_imports(script)
    print("Base85 encode and decode")
    script = encode_decode(script)
    print("Imports at the top")
    script = top_imports(script)
    print("End obfuscation")
    return script

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, type=str)
    parser.add_argument('-o', '--output', required=True, type=str)

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        script = f.read()

    with open(args.output, "w", encoding='utf-8') as f:
        f.write(obfuscate(script))
