
# 对知识库重整，将知识库转化为树形结构


def encode_tree(knowledge):
    index, root_index = 1, None
    tree = []
    tree, index = encode(knowledge, tree, index, root_index)
    return tree

def encode(knowledge, tree, index, father_index):
    if knowledge == {}:
        return tree, index
    for key in list(knowledge.keys()):
        tree.append({"id":index, "content":key, "father_id":father_index})
        index += 1
        tree, index = encode(knowledge[key], tree, index, index - 1)
    return tree, index






def decode_tree(knowledge_tree):
    knowledge = {}
    for k in knowledge_tree:
        key = f"{k['id']};{k['content']}"
        if k['father_id'] == None:
            knowledge[key] = {}
        else:
            _, knowledge = decode(knowledge, key, k['father_id'])
    
    knowledge = simplify(knowledge)
    return knowledge

def decode(knowledge, key, father_id):
    if knowledge == {}:
        return False, knowledge
    for k in list(knowledge.keys()):
        if str(father_id) == k.split(";")[0]:
            knowledge[k][key] = {}
            return True, knowledge
        if_add, knowledge[k] = decode(knowledge[k], key, father_id)
        if if_add:
            return True, knowledge
    return False, knowledge

def simplify(knowledge):
    if knowledge == {}:
        return knowledge
    for k in list(knowledge.keys()):
        new_k = k.split(";")[-1]
        knowledge[new_k] = knowledge[k]
        del knowledge[k]
        knowledge[new_k] = simplify(knowledge[new_k])
    return knowledge