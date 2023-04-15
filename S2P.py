from json import load
import math
import random

ZIPPATH=r"C:\A\B\C"
OUTPATH=r"C:\A\B\C\E\D"
S2PSYSVAL_ANS="S2PSYSVAL__ans__"
file=open(ZIPPATH+"\\project.json",encoding="utf-8")
js=load(file)
output=open(OUTPATH+"\\output.py",encoding="utf-8",mode='w')

#宣言している変数名。
hensu_dict={}

#変数名の空白をアンダーバーに変える。
def S2UL(st:str)->str:
    return st.replace(" ","_")
#int型だったら、そのまま、str型だったら「""」を付け足す関数
def check_int_or_str(checkval)->(int|str):
    if type(checkval)==int or type(checkval)==float:
        return checkval
    else:
        if(checkval.isdigit()):return checkval

        if checkval in hensu_dict:
            return S2UL(checkval)
        else:
            return f'"{checkval}"'

#import
output.write("import math\n")
output.write("import random\n")\
#変数宣言
for i in js["targets"][0]["variables"]:
    output.write(f'{S2UL(js["targets"][0]["variables"][i][0])} = {check_int_or_str(js["targets"][0]["variables"][i][1])}\n')
    hensu_dict[js["targets"][0]["variables"][i][0]]="exsist"#存在していることのみを知らせる。

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

#ネストを一つ下げる。
def nest_down():
    global nestcnt,neststack,nextpoint
    if(nestcnt>0):
        nestcnt-=1
    if(len(neststack)<=0):return
    if(neststack[-1][0]!=None):
        nextpoint=opes[neststack[-1][0]]
        if(neststack[-1][1]=="else"):
            output.write(f'{" "*(nestcnt*4)}else:\n')
            nestcnt+=1
    else:#None
            #さらにネストDOWN
        del neststack[-1]
        nextpoint="S2P_THE_END"#終了フラグ(先にある場合は上書きされる。)
        nest_down()
    if(len(neststack)>0):    
        del neststack[-1]
    return

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
        case "operator_mod":
            hugo="%"
        case "operator_mathop":
            
            match opes[condition_point]["fields"]["OPERATOR"][0]:
                case "floor":mathkansu="math.floor"
                case "abs": mathkansu="abs"
                case "ceiling":mathkansu="math.ceil"
                case "sin":mathkansu="math.sin"
                case "cos":mathkansu="math.cos"
                case "tan":mathkansu="math.tan"
                case "log":mathkansu="math.log"
                case "10 ^":mathkansu="10**"
            return f'{mathkansu}({check_ope_or_lite(opes[condition_point]["inputs"]["NUM"])})'
        case "operator_random":
            return f'random.randint({check_ope_or_lite(opes[condition_point]["inputs"]["FROM"])},{check_ope_or_lite(opes[condition_point]["inputs"]["TO"])})'
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
    
    
    if hugo in ["+","-","*","/","%"]:
        iptwrd="NUM"
    else:
        iptwrd="OPERAND"
    
    op1=check_ope_or_lite(opes[condition_point]["inputs"][f"{iptwrd}1"])
    op2=check_ope_or_lite(opes[condition_point]["inputs"][f"{iptwrd}2"])

    return f'({op1} {hugo} {op2})'

nextpoint=beginpoint
writestring=""

neststack=[]#ネストの次のポイント。nullの時はNoneが入る。
nestcnt=0#ネストのカウント

while True:
    ts=nextpoint["opcode"]
    match ts:
        case "looks_say":
            writestring=f'print({check_ope_or_lite(nextpoint["inputs"]["MESSAGE"])})\n'
        case "sensing_askandwait":
            writestring=f'{S2PSYSVAL_ANS} = input({check_ope_or_lite(nextpoint["inputs"]["QUESTION"])})\n'
        case "control_if_else":#if-else文
            neststack.append([nextpoint["inputs"]["SUBSTACK2"][1],"else"])
            neststack.append([nextpoint.get("next",{"next":None}),"next"])
            writestring=f'if {write_operator_hikaku(nextpoint["inputs"]["CONDITION"][1])}:\n'
            nextpoint=opes[nextpoint["inputs"]["SUBSTACK"][1]]
            output.write(f'{" "*(nestcnt*4)}{writestring}')
            nestcnt+=1
            continue
        case "control_if":#if
            neststack.append([nextpoint.get("next",{"next":None}),"next"])
            writestring=f'if {write_operator_hikaku(nextpoint["inputs"]["CONDITION"][1])}:\n'
            nextpoint=opes[nextpoint["inputs"]["SUBSTACK"][1]]
            output.write(f'{" "*(nestcnt*4)}{writestring}')
            nestcnt+=1
            continue
        case "control_repeat":#for
            neststack.append([nextpoint.get("next",{"next":None}),"next"])
            writestring=f'for i in range({check_ope_or_lite(nextpoint["inputs"]["TIMES"])}):\n'
            nextpoint=opes[nextpoint["inputs"]["SUBSTACK"][1]]
            output.write(f'{" "*(nestcnt*4)}{writestring}')
            nestcnt+=1
            continue
        case "control_repeat_until":#while(!hoge)
            neststack.append([nextpoint.get("next",{"next":None}),"next"])
            writestring=f'while not{write_operator_hikaku(nextpoint["inputs"]["CONDITION"][1])}:\n'
            nextpoint=opes[nextpoint["inputs"]["SUBSTACK"][1]]
            output.write(f'{" "*(nestcnt*4)}{writestring}')
            nestcnt+=1
            continue
        case "control_forever":#while(1)
            neststack.append([None,"next"])
            writestring="while True:\n"
            nextpoint=opes[nextpoint["inputs"]["SUBSTACK"][1]]
            output.write(f'{" "*(nestcnt*4)}{writestring}')
            nestcnt+=1
            continue
        case "data_setvariableto":#代入
            writestring=f'{S2UL(nextpoint["fields"]["VARIABLE"][0])} = {check_ope_or_lite(nextpoint["inputs"]["VALUE"])}\n'
        case "data_changevariableby":#値+
            writestring=f'{S2UL(nextpoint["fields"]["VARIABLE"][0])} += {check_ope_or_lite(nextpoint["inputs"]["VALUE"])}\n'
        
    output.write(f'{" "*(nestcnt*4)}{writestring}')

    if nextpoint["next"]==None:
        if(neststack.__len__()==0):
            break#ネスト0
        nest_down()
        #(下げた結果)
        if(nextpoint=="S2P_THE_END"):
            break#ネスト0&&next==null
    else:
       nextpoint=opes[nextpoint["next"]]
output.close()
