import json
import pdfplumber
import cn2an
from ours.organize_knowledge import encode_tree
import argparse
import os

# pdf文档 -> 过滤后的规则






def if_line_begin_with_id(before_lines, line):
    if line == "":
        return False, ""
    # 1.1.1 规则、1.1.1规则、1 规则、1规则、1.1.1、规则
    is_number=True
    id = ""
    for i, s in enumerate(line.split(".")):
        if s.isdigit():
            id += s + "."
        else:
            is_number = False
            break
    if is_number:  # 1.1.1、1
        if id[:-1].isdigit():  # 1
            return False, ""
        return True, id[:-1]  # 1.1.1
    for c in line.split(".")[i]:  # 1.1.1规则、1规则
        if c.isdigit():
            id += c
        else:
            break
    if id != "":
        if before_lines != "" and before_lines[-1] != "。":  # 处理数字出现在规则中，但在一行开头的特殊情况
            return False, ""
        return True, id
    
    # 第一张、第一节、第一条、...
    if line[0] == "第":
        a, b = 1, float("inf")
        if "章" in line and line.index("章") < b:
            a, b = 1, line.index("章")
        if "节" in line and line.index("节") < b:
            a, b = 1, line.index("节")
        if "条" in line and line.index("条") < b:
            a, b = 1, line.index("条")
        s = line[a:b]
        if s.isdigit():
            return True, line[:b+1]
        try:
            cn2an.cn2an(s)
            return True, line[:b+1]
        except:
            return False, ""
    return False, ""




def get_setting(s, knowledge):
    market, market_num, variety, variety_num = "", 0, "", 0
    tree = encode_tree(knowledge)

    markets, varieties = [], []
    # 所有的品种/业务有：
    # variety = ["债券","可转债","股票","创业板","基金","基础设施基金","权证","存托凭证","股票质押式回购交易","融资融券交易","资产管理计划份额转让","资产证券化","深港通","质押式报价回购交易"]
    for key in tree:
        if "交易市场" == key['content'].split(":")[0]:
            markets.append(key['content'].split(":")[-1])
            
        elif "品种" in key['content'].split(":")[0] or "业务" == key['content'].split(":")[0]:
            varieties.append(key['content'].split(":")[-1])

    markets = list(set(markets))
    varieties = list(set(varieties))

    market, variety = "", ""
    for value in markets:
        value_count = s.count(value)
        if value_count > market_num:
            market_num = value_count
            market = value
    
    s = s.strip()
    for value in varieties:
        # 统计时只统计标题
        paper = s.split("\n")
        i = 0
        last_line = ""
        while i < len(paper) and not if_line_begin_with_id(last_line, paper[i])[0]:
            last_line = paper[i]
            i += 1
        if i == 0 or i == len(paper):
            i = 2
        paper = "\n".join(paper[:i])
        value_count = paper.count(value)
        if value_count >= 1 and len(value) > len(variety):  # 选最长的，也就是最细粒度的
            variety = value
            variety_num = value_count

    if market_num == 0:
        if "\n".join(s.split("\n")).count("深圳") > "\n".join(s.split("\n")).count("上海"):
            market = "深圳证券交易所"
        elif "\n".join(s.split("\n")).count("深圳") < "\n".join(s.split("\n")).count("上海"):
            market = "上海证券交易所"
        else:
            if "\n".join(s.split("\n")).count("深交所") > "\n".join(s.split("\n")).count("上交所"):
                market = "深圳证券交易所"
            elif "\n".join(s.split("\n")).count("深交所") < "\n".join(s.split("\n")).count("上交所"):
                market = "上海证券交易所"
            else:
                market = "证券交易所"

    return {"market": market, "variety": variety}





def document_to_rules(file, knowledge):
    """
    将pdf/txt文档按规则分割，并提取market和product
    """
    # 确保文件存在
    assert os.path.exists(file), f"File {file} not found."
    if file.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    else:
        text = open(file, "r", encoding="utf-8").read()
    text = text.replace("〇", "零").replace("：", ":").replace("︰", "")  # 符号标准化

    # s: "id: rule\nid: rule\n..."
    s = ""
    for line in text.split("\n"):
        line = line.strip()
        if line == "":
            continue
        if line.find("附件") == 0:
            continue
        if "—" in line or line.isdigit():  # 页码
            continue
        begin_with_id, id = if_line_begin_with_id(s, line)
        if begin_with_id:
            si = line[len(id):].replace(" ", "")
            s += "\n" + id + " " + si
        else:
            s += line.replace(" ", "")
    
    setting = get_setting(text, knowledge)
    
    rules = []
    last_line = ""
    for line in s.split("\n"):
        line = line.strip()
        if line == "":
            continue
        begin_with_id, id = if_line_begin_with_id(last_line, line)
        last_line = line
        if "章" in line or "节" in line:
            continue
        if begin_with_id:
            rules.append({"id": id, "text": line[len(id):].strip(), "type": ""})
    
    return rules, setting













if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, default="../corpus/document/深圳证券交易所债券交易规则.pdf")
    args = parser.parse_args()
    knowledge = json.load(open("../corpus/domain_knowledge/knowledge_tree.json", "r", encoding="utf-8"))
    rules, setting = document_to_rules(file=args.file, knowledge=knowledge)

    json.dump(rules, open("cache/rule_filtering_input.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    json.dump(setting, open("cache/setting.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)