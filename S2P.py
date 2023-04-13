from json import load

ZIPPATH=r"C:\A\B\C"
OUTPATH=r"C:\A\B\E\D"
S2PSYSVAL_ANS="S2PSYSVAL__ans__"
file=open(ZIPPATH+"\\project.json",encoding="utf-8")
js=load(file)
output=open(OUTPATH+"\\output.py",encoding="utf-8",mode='w')
#変数名の空白をアンダーバーに変える。
def S2UL(st:str)->str:
    return st.replace(" ","_")
#int型だったら、そのまま、str型だったら「""」を付け足す関数
def check_int_or_str(checkval):
    if type(checkval)==int:
        return checkval
    else:
        if(checkval.isdigit()):return checkval
        return f'"{checkval}"'

#変数宣言
for i in js["targets"][0]["variables"]:
    output.write(f'{S2UL(js["targets"][0]["variables"][i][0])} = {check_int_or_str(js["targets"][0]["variables"][i][1])}\n')

#命令がいっぱいあるところ。
opes=js["targets"][1]["blocks"]
beginpoint=""
for i in opes:
    if opes[i]["opcode"]=="event_whenflagclicked":
        beginpoint=opes[i]
        break

#opeかリテラルかの判断(自動でcheck_int_or_strを呼び出す)し、展開結果を返す。
def check_ope_or_lite(check):
    if(type(check[1])==str):
        return write_operator_hikaku(check[1])
    else:
        return check_int_or_str(check[1][1])

#operator_XXX の処理。やっぱり再帰が一番!
def write_operator_hikaku(condition_point):
    hugo=""
    match opes[condition_point]["opcode"]:
        case "operator_and":
            hugo="and"
        case "operator_or":
            hugo="or"
        case "operator_equals":
            hugo="=="
        case "operator_gt":
            hugo=">"
        case "operator_lt":
            hugo="<"
        case "operator_add":
            hugo="+"
        case "operator_subtract":
            hugo="-"
        case "operator_multiply":
            hugo="*"
        case "operator_divide":
            hugo="/"
        case "sensing_answer":
            return S2PSYSVAL_ANS
        case "operator_not":
            return f'(not {check_ope_or_lite(opes[condition_point]["inputs"][f"OPERAND"])})'
        case "operator_length":
            return f'({check_ope_or_lite(opes[condition_point]["inputs"]["STRING"])}.__len__())'
        case "operator_letter_of":
            return f'({check_ope_or_lite(opes[condition_point]["inputs"]["STRING"])})[{check_ope_or_lite(opes[condition_point]["inputs"]["LETTER"])} - 1]'
        case _:
            pass
    
    
    if hugo=="+" or hugo=="-" or hugo=="*" or hugo=="/":
        iptwrd="NUM"
    else:
        iptwrd="OPERAND"
    
    op1=check_ope_or_lite(opes[condition_point]["inputs"][f"{iptwrd}1"])
    op2=check_ope_or_lite(opes[condition_point]["inputs"][f"{iptwrd}2"])

    return f'({op1} {hugo} {op2})'

nextpoint=beginpoint
writestring=""
while True:
    ts=nextpoint["opcode"]
    match ts:
        case "looks_say":
            writestring=f'print({check_ope_or_lite(nextpoint["inputs"]["MESSAGE"])})\n'
        case "sensing_askandwait":
            writestring=f'{S2PSYSVAL_ANS} = input({check_ope_or_lite(nextpoint["inputs"]["QUESTION"])})\n'
        case "control_if":#if文
            writestring=write_operator_hikaku(nextpoint["inputs"]["CONDITION"][1])
        case "data_setvariableto":#代入
            writestring=f'{S2UL(nextpoint["fields"]["VARIABLE"][0])} = {check_ope_or_lite(nextpoint["inputs"]["VALUE"])}\n'
        case "data_changevariableby":#値+
            writestring=f'{S2UL(nextpoint["fields"]["VARIABLE"][0])} += {check_ope_or_lite(nextpoint["inputs"]["VALUE"])}\n'
    if nextpoint["next"]==None:
        break
    else:
       output.write(writestring)
       nextpoint=opes[nextpoint["next"]]
output.close()
