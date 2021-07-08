#!/usr/bin/env python3

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Nazev programu: interpret.py                            #
# Autor: Pavel Bednar (xbedna73)                          #
# Skola: FIT VUT v Brne                                   #
# Zadani: Implementace 2. casti IPP projektu 2019/2020,   #
#         zadani viz soubor README.md                     #
# Jazyk: Python 3.8.2                                     #
# Datum vytvoreni: 2020-04-03                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import sys
import re
import xml.etree.ElementTree as x2t

#
# Funkce, ktera vytiskne napovedu.
#
def printHelp():
    print("+-------------------------------------------------------+")
    print("| Napoveda k programu interpet.py                       |")
    print("+-------------------------------------------------------+")
    print("| Vstup: kod v IPPcode20 popripade vstup                |")
    print("| Vystup: interpretace programu v jazyce IPPcode20      |")
    print("+-------------------------------------------------------+")
    print("| Parametry:                                            |")
    print("|  --help  --source  --input                            |")
    print("+-------------------------------------------------------+")
    print("| Navratove kody:                                       |")
    print("|  0 : program probehl bez chyby                        |")
    print("|  10: chybny nebo chybna kombinace argumentu           |")
    print("|  11: chyba pri otevirani vstupnich souboru            |")
    print("|                                                       |")
    print("|  31: chybny XML format                                |")
    print("|  32: neocekavana struktura XML                        |")
    print("|                                                       |")
    print("|  52: chyba pri semantickych kontrolach                |")
    print("|  53: spatne typy operandu (behova chyba)              |")
    print("|  54: pristup k neexistujici promenne (behova chyba)   |")
    print("|  55: neexistujici ramec (behova chyba)                |")
    print("|  56: chybejici hodnota (behova chyba)                 |")
    print("|  57: chybna hodnota operandu (behova chyba)           |")
    print("|  58: chybna prace s retezcem (behova chyba)           |")
    print("+-------------------------------------------------------+")
    exit(0)

#
# Funkce, ktera overi syntaktickou spravnost argumentu.
#
def argType(arg, arg_cnt):
    is_help = re.match('^--help$', arg)
    arg = re.search('^--(input|source)=(.+)$', arg)
    if is_help:
        if arg_cnt == 1:
            printHelp()
        else:
            exit(10)
    elif arg:
        arg_type = arg.group(1)
        arg_value = arg.group(2)
    else:
        exit(10)
    return arg_type, arg_value

#
# Funkce, ktera overi semantickou spravnost argumentu a vrati slovnik
# spravnych parametru.
#
def argCheck(arg_array):
    arg_dict = {}
    for arg in arg_array[1:]:
        arg_type, arg_value = argType(arg, len(arg_array) - 1)
        arg_dict[arg_type] = arg_value
    if not 'input' in arg_dict:
        arg_dict['input'] = None
    if not 'source' in arg_dict:
        arg_dict['source'] = None
    if arg_dict['input'] == None  and arg_dict['source'] == None:
        exit(10)
    return arg_dict

#
# Funkce, ktera vrati zdrojovy soubor ve stromove strukture a zjisti jestli
# je potencialni vstup ze STDIN nebo z nejakeho souboru.
#
def getInputs():
    arg_dict = argCheck(sys.argv)
    if arg_dict['source'] != None:
        try:
            arg_tree = x2t.parse(arg_dict['source'])
        except x2t.ParseError:
            exit(31)
        except:
            exit(11)
        root = arg_tree.getroot()
    if arg_dict['source'] == None:
        lines = ''
        for line in sys.stdin:
            lines += line
        try:
            root = x2t.fromstring(lines)
        except x2t.ParseError:
            exit(31)
        except:
            exit(11)
    ret_input = {}
    ret_input['input'] = arg_dict['input']
    return root, ret_input

#
# Funkce, ktera zkontroluje jestli argument je typu label a jestli je
# ve slovniku navesti.
#
def isDefinedLabelOrExit(arg, label_dic):
    arg_ok = re.search('^[_,-,$,&,%,*,!,?,a-zA-Z]+[_,-,$,&,%,*,!,?,a-zA-Z,0-9]*$', arg)
    if not arg_ok:
        exit(32)
    if not arg_ok.group(0) in label_dic:
        exit(52)

#
# Funkce, ktera zkontroluje jestli argument je typu label a jestli jeste neni
# ve slovniku navesti.
#
def isLabelOrExit(arg, label_dic):
    arg_ok = re.search('^[_,-,$,&,%,*,!,?,a-zA-Z]+[_,-,$,&,%,*,!,?,a-zA-Z,0-9]*$', arg)
    if not arg_ok:
        exit(32)
    if arg_ok.group(0) in label_dic:
        exit(52)

#
# Funkce, ktera zkontroluje spravnost navesti a pripadne ho vlozi do
# slovniku navesti.
#
def checkLabel(arg_array, label_dic):
    numOfArgsCheck(arg_array, 1)
    argTypesCheck(arg_array, 1, {'label'})

    isLabelOrExit(arg_array['arg1']['arg'], label_dic)
    label_dic[arg_array['arg1']['arg']] = arg_array['order']
    return label_dic

#
# Funkce, ktera zkontroluje syntaktickou spravnost XML vstupu a inicializuje
# slovnik navesti.
#
def XMLsyntaxAndLabelCheck(root):
    if root.tag != 'program':
        exit(32)
    if len(root.attrib) < 1 and len(root.attrib) > 3:
        exit(32)
    if len(root.attrib) == 1:
        if not 'language' in root.attrib:
            exit(32)
    if len(root.attrib) == 2:
        if not 'language' in root.attrib or (not 'name' in root.attrib and not 'description' in root.attrib):
            exit(32)
    if len(root.attrib) == 3:
        if not 'language' in root.attrib or not 'name' in root.attrib or not 'description' in root.attrib:
            exit(32)
    if root.attrib['language'].lower() != 'ippcode20':
        exit(32)
    ret_array = {}
    label_dic = {}
    order_array1 = {}
    order_array2 = {}
    i = 0
    for child in root:
        if child.tag != 'instruction':
            exit(32)
        if len(child.attrib) != 2:
            exit(32)
        if not 'order' in child.attrib:
            exit(32)
        if not child.attrib['order'].isnumeric():
            exit(32)
        order_array1[i] = child.attrib['order']
        order_array2[child.attrib['order']] = True
        i += 1
        if not 'opcode' in child.attrib:
            exit(32)
        arg_array = {'order': child.attrib['order'], 'opcode': child.attrib['opcode']}
        j = 1
        for sec_child in child:
            act_arg = 'arg' + str(j)
            j += 1
            if sec_child.tag != act_arg:
                exit(32)
            if len(sec_child.attrib) != 1:
                exit(32)
            if not 'type' in sec_child.attrib:
                exit(32)
            arg_array[act_arg] = {'arg': sec_child.text, 'type': sec_child.attrib['type']}
        ret_array[int(child.attrib['order'])] = arg_array
        if arg_array['opcode'].upper() == 'LABEL':
            label_dic = checkLabel(arg_array, label_dic)
    if len(order_array1) != len(order_array2):
        exit(32)
    return ret_array, label_dic

#
# Fuknce, ktera vrati vrchol zasobniku.
#
def stackTop(stack):
    if len(stack) > 0:
        return stack[len(stack) - 1]

#
# Funkce, ktera zkontroluje, že promenna arg je typu var, pokud ano vrati
# True, jeji nazev a frame, pokud ne ukonci program.
#
def isVar(arg):
    arg_var = re.search('^[G,L,T]F@[_,-,$,&,%,*,!,?,a-zA-Z]+[_,-,$,&,%,*,!,?,a-zA-Z,0-9]*$', arg)
    if arg_var:
        divide = re.search('^(.*)@(.*)', arg_var.group(0))
        frame = divide.group(1)
        var = divide.group(2)
        return var, frame
    else:
        exit(32)

#
# Fuknce, ktera ukonci program pokud arg neni typu int nebo vrati spravne otypovany arg.
#
def isInt(arg):
    try:
        ret_int = int(arg)
    except:
        exit(32)
    return ret_int

#
# Fuknce, ktera ukonci program pokud arg neni typu bool nebo vrati spravne otypovany arg.
#
def isBool(arg):
    arg_bool = re.search('^true|false$', arg)
    if arg_bool:
        if arg_bool.group(0) == 'true':
            return True
        if arg_bool.group(0) == 'false':
            return False
    else:
        exit(32)

#
# Fuknce, ktera ukonci program pokud arg neni typu string nebo vrati spravne otypovany arg.
#
def isString(arg):
    if arg == None:
        arg = ''
    arg_string_comment_ws = re.search('\s|#', arg)
    if arg_string_comment_ws:
        exit(32)
    arg_string = re.search('^(\\\\[0-9]{3}|[^\\\\])*$', arg)
    if arg_string:
        arg_string_esc = re.findall('(\\\\[0-9]{3})', arg)
        for each_esc in arg_string_esc:
            conv_esc = chr(int(each_esc[1:]))
            arg = arg.replace(each_esc, conv_esc)
        return arg
    else:
        exit(32)

#
# Fuknce, ktera ukonci program pokud arg neni typu nil nebo vrati spravne otypovany arg.
# '\00nil' je oznaceni hodnoty nil v pametovych ramcich, a to protoze pokud bude tento retezec
# v nejakem pametovem ramci, tak nemuze byt typu bool, int ani string.
#
def isNil(arg):
    arg_nil = re.search('^nil$', arg)
    if arg_nil:
        return '\00nil'
    else:
        exit(32)

#
# Funkce, ktera zkontroluje jestli argument arg_arg je typu arg_type, pokud ne program se
# ukonci, pokud ano tak vrati jeji spravne typovanou hodnotu. Pokud se jedna o typ var, tak
# vrati primo hodnotu promenne nebo pokud nelze precit hodnotu tak ukonci program.
#
def argValuesCheck(arg_type, arg_arg, GF_dic, TF_dic, is_tf_init, LF_stack):
    if arg_type == 'bool':
        return isBool(arg_arg), GF_dic, TF_dic, is_tf_init, LF_stack
    if arg_type == 'int':
        return isInt(arg_arg), GF_dic, TF_dic, is_tf_init, LF_stack
    if arg_type == 'string':
        return isString(arg_arg), GF_dic, TF_dic, is_tf_init, LF_stack
    if arg_type == 'nil':
        return isNil(arg_arg), GF_dic, TF_dic, is_tf_init, LF_stack
    if arg_type == 'var':
        var, frame = isVar(arg_arg)
        return readFromVar(var, frame, GF_dic, TF_dic, is_tf_init, LF_stack), GF_dic, TF_dic, is_tf_init, LF_stack

#
# Fuknce identicka s funkci argValuesCheck, ale vraci navic promennou init ktera znaci jestli
# je promenna v pametovem ramci inicializovana, pokud neni inicializovana tak neukonci program,
# ale do init se vlozi False, jinak bude v init True.
#
def argValuesCheckForTypeFunc(arg_type, arg_arg, GF_dic, TF_dic, is_tf_init, LF_stack):
    init = True
    if arg_type == 'bool':
        return init, isBool(arg_arg), GF_dic, TF_dic, is_tf_init, LF_stack
    if arg_type == 'int':
        return init, isInt(arg_arg), GF_dic, TF_dic, is_tf_init, LF_stack
    if arg_type == 'string':
        return init, isString(arg_arg), GF_dic, TF_dic, is_tf_init, LF_stack
    if arg_type == 'nil':
        return init, isNil(arg_arg), GF_dic, TF_dic, is_tf_init, LF_stack
    if arg_type == 'var':
        var, frame = isVar(arg_arg)
        if frame == 'GF':
            if not var in GF_dic:
                exit(54)
            if GF_dic[var] == None:
                init = False
            value = GF_dic[var]
        if frame == 'TF':
            if is_tf_init == False:
                exit(55)
            if not var in TF_dic:
                exit(54)
            if TF_dic[var] == None:
                init = False
            value = TF_dic[var]
        if frame == 'LF':
            if len(LF_stack) == 0:
                exit(55)
            if not var in stackTop(LF_stack):
                exit(54)
            if stackTop(LF_stack)[var] == None:
                init = False
            value = stackTop(LF_stack)[var]
        return init, value, GF_dic, TF_dic, is_tf_init, LF_stack

#
# Funkce, ktera zkontroluje jestli ma instrukce arg_array pozadovany pocet argumentu arg_cnt.
#
def numOfArgsCheck(arg_array, arg_cnt):
    if len(arg_array) != arg_cnt + 2:
        exit(32)

#
# Funkce, ktera zkontroluje jestli je arg_num-ty argument instrukce arg_array typu z
# povolene mnoziny typu type_array.
#
def argTypesCheck(arg_array, arg_num, type_array):
    arg = 'arg' + str(arg_num)
    if not arg_array[arg]['type'] in type_array:
        exit(32)

#
# Funkce, ktera vypise zakladni debugovaci informace na stderr.
#
def stderrDebug(instruction_order, instruction_cnt, GF_dic, LF_stack, TF_dic, is_tf_init, call_stack, label_dic, data_stack):
    print('-------------------------------------------------------', file=sys.stderr)
    print('--- BASIC INFO ---', file=sys.stderr)
    print('Executed instructions: ', end='', file=sys.stderr)
    print(instruction_cnt, file=sys.stderr)
    print('Actual instruction order: ', end='', file=sys.stderr)
    print(instruction_order, file=sys.stderr)
    print('', file=sys.stderr)
    print('--- FRAMES ---', file=sys.stderr)
    print('GLOBAL FRAME: ', end='', file=sys.stderr)
    print(GF_dic, file=sys.stderr)
    print('LOCAL FRAME: ', end='', file=sys.stderr)
    print(LF_stack, end='', file=sys.stderr)
    print(' <- TOP', file=sys.stderr)
    if is_tf_init == True:
        print('TEMPORARY FRAME: ', end='', file=sys.stderr)
        print(TF_dic, file=sys.stderr)
    else:
        print('TEMPORARY FRAME: None', file=sys.stderr)
    print('', file=sys.stderr)
    print('--- CALLS ---', file=sys.stderr)
    print('CALL STACK: ', end='', file=sys.stderr)
    print(call_stack, end='', file=sys.stderr)
    print(' <- TOP', file=sys.stderr)
    print('LABELS: ', end='', file=sys.stderr)
    print(label_dic, file=sys.stderr)
    print('', file=sys.stderr)
    print('--- DATA ---', file=sys.stderr)
    print('DATA STACK: ', end='', file=sys.stderr)
    print(data_stack, end='', file=sys.stderr)
    print(' <- TOP', file=sys.stderr)
    print('', file=sys.stderr)
    print('-------------------------------------------------------', file=sys.stderr)

#
# Funkce, ktera vraci hodnotu kterou precetla instrukce read.
#
def doRead(input_file, arg2_arg, input_from_file):
    nil = False
    if input_file['input'] == None:
        try:
            inpt = input()
        except:
            nil = True
    else:
        try:
            inpt = input_from_file.readline().rstrip()
        except:
            nil = True

    if nil == False:
        if arg2_arg == 'int':
            try:
                value = int(inpt)
            except:
                nil = True
        elif arg2_arg == 'bool':
            inpt_l = inpt.lower()
            if inpt_l == 'true':
                value = True
            else:
                value = False
        elif arg2_arg == 'string':
            try:
                value = isString(inpt)
            except:
                nil = True
        else:
            exit(32)
    if nil:
        return '\00nil'
    else:
        return value

#
# Fuknce, ktera zadefinuje promennou.
#
def defVar(var, frame, GF_dic, TF_dic, is_tf_init, LF_stack):
    if frame == 'GF':
        if var in GF_dic:
            exit(52)
        GF_dic[var] = None
    if frame == 'TF':
        if is_tf_init == False:
            exit(55)
        if var in TF_dic:
            exit(52)
        TF_dic[var] = None
    if frame == 'LF':
        if len(LF_stack) == 0:
            exit(55)
        if var in stackTop(LF_stack):
            exit(52)
        stackTop(LF_stack)[var] = None
    return GF_dic, TF_dic, LF_stack

#
# Funkce, ktera cte z promenne, a to co precte vrati.
#
def readFromVar(var, frame, GF_dic, TF_dic, is_tf_init, LF_stack):
    if frame == 'GF':
        if not var in GF_dic:
            exit(54)
        if GF_dic[var] == None:
            exit(56)
        value = GF_dic[var]
    if frame == 'TF':
        if is_tf_init == False:
            exit(55)
        if not var in TF_dic:
            exit(54)
        if TF_dic[var] == None:
            exit(56)
        value = TF_dic[var]
    if frame == 'LF':
        if len(LF_stack) == 0:
            exit(55)
        if not var in stackTop(LF_stack):
            exit(54)
        if stackTop(LF_stack)[var] == None:
            exit(56)
        value = stackTop(LF_stack)[var]
    return value

#
# Funkce, ktera do promenne zapise.
#
def writeToVar(value, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack):
    if frame == 'GF':
        if not var in GF_dic:
            exit(54)
        GF_dic[var] = value
    if frame == 'TF':
        if is_tf_init == False:
            exit(55)
        if not var in TF_dic:
            exit(54)
        TF_dic[var] = value
    if frame == 'LF':
        if len(LF_stack) == 0:
            exit(55)
        if not var in stackTop(LF_stack):
            exit(54)
        stackTop(LF_stack)[var] = value
    return GF_dic, TF_dic, LF_stack

#
# Funkce, ktera provadi instrukce. Boolovsky prepinac dbg slouzi k zapnuti/vypnuti
# debugovacich informaci.
#
def doInstructions(dbg):
    xml_root, input_file = getInputs()
    if input_file['input'] != None:
        input_open_file = open(input_file['input'], 'r')
    else:
        input_open_file = None
    instructions_array, label_dic = XMLsyntaxAndLabelCheck(xml_root)
    instructions_array_sorted = sorted(instructions_array)
    GF_dic = {}
    TF_dic = {}
    is_tf_init = False
    LF_stack = []
    call_stack = []
    data_stack = []
    is_output = False
    exit_value = 0
    write_output = ''
    instruction = 0
    symb = {'var', 'int', 'bool', 'string', 'nil'}
    while instruction < len(instructions_array):
        if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'MOVE':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 2)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, symb)

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            GF_dic, TF_dic, LF_stack = writeToVar(value2, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'CREATEFRAME':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 0)
            is_tf_init = True
            TF_dic = {}

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'PUSHFRAME':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 0)
            if is_tf_init == False:
                exit(55)
            is_tf_init = False
            LF_stack.append(TF_dic)
            TF_dic = {}

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'POPFRAME':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 0)
            if len(LF_stack) == 0:
                exit(55)
            is_tf_init = True
            TF_dic = stackTop(LF_stack)
            LF_stack.pop()

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'DEFVAR':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 1)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            GF_dic, TF_dic, LF_stack = defVar(var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() in {'CALL', 'JUMP'}:
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 1)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'label'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            isDefinedLabelOrExit(arg_arg, label_dic)

            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'CALL':
                call_stack.append(instruction + 1)
            instruction = instructions_array_sorted.index(int(label_dic[arg_arg])) - 1

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'RETURN':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 0)
            if len(call_stack) == 0:
                exit(56)

            instruction = stackTop(call_stack) - 1
            call_stack.pop()

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'EXIT':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 1)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'int', 'var'})

            arg_type = instructions_array[instructions_array_sorted[instruction]]['arg1']['type']
            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            value, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg_type, arg_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            if not isinstance(value, int):
                exit(57)
            if value < 0 or value > 49:
                exit(57)
            exit_value = value
            instruction = len(instructions_array)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'READ':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 2)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'type'})

            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value = doRead(input_file, arg2_arg, input_open_file)
            GF_dic, TF_dic, LF_stack = writeToVar(value, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() in {'WRITE', 'DPRINT'}:
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 1)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, symb)

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']
            arg_type = instructions_array[instructions_array_sorted[instruction]]['arg1']['type']

            value, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg_type, arg_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            if value == '\00nil':
                value = ''
            if value == True and value != 1:
                value = 'true'
            if value == False and value != 0:
                value = 'false'

            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'WRITE':
                is_output = True
                write_output += str(value)
            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'DPRINT':
                print(value, file=sys.stderr)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'PUSHS':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 1)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, symb)

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']
            arg_type = instructions_array[instructions_array_sorted[instruction]]['arg1']['type']

            value, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg_type, arg_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            data_stack.append(value)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'POPS':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 1)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            if len(data_stack) == 0:
                exit(56)
            else:
                GF_dic, TF_dic, LF_stack = writeToVar(stackTop(data_stack), var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)
                data_stack.pop()

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() in {'ADD', 'SUB', 'MUL', 'IDIV'}:
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 3)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'var', 'int'})

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 3, {'var', 'int'})

            arg3_type = instructions_array[instructions_array_sorted[instruction]]['arg3']['type']
            arg3_arg = instructions_array[instructions_array_sorted[instruction]]['arg3']['arg']

            value3, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg3_type, arg3_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            if not isinstance(value2, int) or isinstance(value2, bool):
                exit(53)
            if not isinstance(value3, int) or isinstance(value3, bool):
                exit(53)

            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'ADD':
                GF_dic, TF_dic, LF_stack = writeToVar(value2 + value3, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)
            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'SUB':
                GF_dic, TF_dic, LF_stack = writeToVar(value2 - value3, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)
            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'MUL':
                GF_dic, TF_dic, LF_stack = writeToVar(value2 * value3, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)
            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'IDIV':
                if value3 == 0:
                    exit(57)
                GF_dic, TF_dic, LF_stack = writeToVar(int(value2 / value3), var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() in {'LT', 'GT', 'EQ'}:
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 3)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'var', 'int', 'bool', 'string'})

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 3, {'var', 'int', 'bool', 'string'})

            arg3_type = instructions_array[instructions_array_sorted[instruction]]['arg3']['type']
            arg3_arg = instructions_array[instructions_array_sorted[instruction]]['arg3']['arg']

            value3, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg3_type, arg3_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            if isinstance(value2, int) and not isinstance(value2, bool):
                value2_type = 'int'
            if isinstance(value2, bool):
                value2_type = 'bool'
            if isinstance(value2, str) and value2 != '\00nil':
                value2_type = 'string'
            if value2 == '\00nil':
                if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() != 'EQ':
                    exit(53)
                value2_type = 'nil'
            if isinstance(value3, int) and not isinstance(value3, bool):
                value3_type = 'int'
            if isinstance(value3, bool):
                value3_type = 'bool'
            if isinstance(value3, str) and value3 != '\00nil':
                value3_type = 'string'
            if value3 == '\00nil':
                if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() != 'EQ':
                    exit(53)
                value3_type = 'nil'

            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'LT':
                if value2_type != value3_type:
                    exit(53)
                GF_dic, TF_dic, LF_stack = writeToVar(value2 < value3, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)
            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'GT':
                if value2_type != value3_type:
                    exit(53)
                GF_dic, TF_dic, LF_stack = writeToVar(value2 > value3, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)
            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'EQ':
                if value2_type != value3_type and value2_type != 'nil' and value3_type != 'nil':
                    exit(53)
                GF_dic, TF_dic, LF_stack = writeToVar(value2 == value3, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() in {'AND', 'OR'}:
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 3)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'bool', 'var'})

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 3, {'bool', 'var'})

            arg3_type = instructions_array[instructions_array_sorted[instruction]]['arg3']['type']
            arg3_arg = instructions_array[instructions_array_sorted[instruction]]['arg3']['arg']

            value3, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg3_type, arg3_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            if not isinstance(value2, bool):
                exit(53)
            if not isinstance(value3, bool):
                exit(53)

            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'AND':
                GF_dic, TF_dic, LF_stack = writeToVar(value2 and value3, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)
            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'OR':
                GF_dic, TF_dic, LF_stack = writeToVar(value2 or value3, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'NOT':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 2)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'bool', 'var'})

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            if not isinstance(value2, bool):
                exit(53)

            GF_dic, TF_dic, LF_stack = writeToVar(not value2, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'INT2CHAR':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 2)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'var', 'int'})

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value2, int) or isinstance(value2, bool):
                exit(53)

            try:
                value_to_write = chr(value2)
            except:
                exit(58)
            GF_dic, TF_dic, LF_stack = writeToVar(value_to_write, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'STRI2INT':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 3)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'var', 'string'})

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value2, str) or value2 == '\00nil':
                exit(53)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 3, {'var', 'int'})

            arg3_type = instructions_array[instructions_array_sorted[instruction]]['arg3']['type']
            arg3_arg = instructions_array[instructions_array_sorted[instruction]]['arg3']['arg']

            value3, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg3_type, arg3_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value3, int) or isinstance(value3, bool):
                exit(53)
            try:
                value_to_write = ord(value2[value3])
            except:
                exit(58)

            GF_dic, TF_dic, LF_stack = writeToVar(value_to_write, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'CONCAT':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 3)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'var', 'string'})

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value2, str) or value2 == '\00nil':
                exit(53)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 3, {'var', 'string'})

            arg3_type = instructions_array[instructions_array_sorted[instruction]]['arg3']['type']
            arg3_arg = instructions_array[instructions_array_sorted[instruction]]['arg3']['arg']

            value3, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg3_type, arg3_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value2, str) or value2 == '\00nil':
                exit(53)

            GF_dic, TF_dic, LF_stack = writeToVar(value2 + value3, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'STRLEN':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 2)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'var', 'string'})

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value2, str) or value2 == '\00nil':
                exit(53)

            GF_dic, TF_dic, LF_stack = writeToVar(len(value2), var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'GETCHAR':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 3)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'var', 'string'})

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value2, str) or value2 == '\00nil':
                exit(53)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 3, {'var', 'int'})

            arg3_type = instructions_array[instructions_array_sorted[instruction]]['arg3']['type']
            arg3_arg = instructions_array[instructions_array_sorted[instruction]]['arg3']['arg']

            value3, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg3_type, arg3_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value3, int) or isinstance(value3, bool):
                exit(53)
            if value3 < 0:
                exit(53)
            try:
                value_to_write = value2[value3]
            except:
                exit(58)

            GF_dic, TF_dic, LF_stack = writeToVar(value_to_write, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'SETCHAR':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 3)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']
            arg_type = instructions_array[instructions_array_sorted[instruction]]['arg1']['type']

            var, frame = isVar(arg_arg)
            value, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg_type, arg_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value, str) or value == '\00nil':
                exit(53)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, {'var', 'int'})

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value2, int) or isinstance(value2, bool):
                exit(53)
            if value2 < 0:
                exit(53)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 3, {'var', 'string'})

            arg3_type = instructions_array[instructions_array_sorted[instruction]]['arg3']['type']
            arg3_arg = instructions_array[instructions_array_sorted[instruction]]['arg3']['arg']

            value3, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg3_type, arg3_arg, GF_dic, TF_dic, is_tf_init, LF_stack)
            if not isinstance(value3, str) or value3 == '\00nil':
                exit(53)

            if value2 > len(value) - 1:
                exit(58)
            if value3 == '':
                exit(58)
            value_to_write = value[:value2] + value3[0] + value[value2 + 1:]

            GF_dic, TF_dic, LF_stack = writeToVar(value_to_write, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'TYPE':
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 2)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'var'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            var, frame = isVar(arg_arg)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, symb)

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            init, value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheckForTypeFunc(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            if init:
                if isinstance(value2, int) and not isinstance(value2, bool):
                    value2_type = 'int'
                if isinstance(value2, bool):
                    value2_type = 'bool'
                if isinstance(value2, str) and value2 != '\00nil':
                    value2_type = 'string'
                if value2 == '\00nil':
                    value2_type = 'nil'
            else:
                value2_type = ''
            GF_dic, TF_dic, LF_stack = writeToVar(value2_type, var, frame, GF_dic, TF_dic, is_tf_init, LF_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() in {'JUMPIFEQ', 'JUMPIFNEQ'}:
            numOfArgsCheck(instructions_array[instructions_array_sorted[instruction]], 3)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 1, {'label'})

            arg_arg = instructions_array[instructions_array_sorted[instruction]]['arg1']['arg']

            isDefinedLabelOrExit(arg_arg, label_dic)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 2, symb)

            arg2_type = instructions_array[instructions_array_sorted[instruction]]['arg2']['type']
            arg2_arg = instructions_array[instructions_array_sorted[instruction]]['arg2']['arg']

            value2, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg2_type, arg2_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            argTypesCheck(instructions_array[instructions_array_sorted[instruction]], 3, symb)

            arg3_type = instructions_array[instructions_array_sorted[instruction]]['arg3']['type']
            arg3_arg = instructions_array[instructions_array_sorted[instruction]]['arg3']['arg']

            value3, GF_dic, TF_dic, is_tf_init, LF_stack = argValuesCheck(arg3_type, arg3_arg, GF_dic, TF_dic, is_tf_init, LF_stack)

            if isinstance(value2, int) and not isinstance(value2, bool):
                value2_type = 'int'
            if isinstance(value2, bool):
                value2_type = 'bool'
            if isinstance(value2, str) and value2 != '\00nil':
                value2_type = 'string'
            if value2 == '\00nil':
                value2_type = 'nil'
            if isinstance(value3, int) and not isinstance(value3, bool):
                value3_type = 'int'
            if isinstance(value3, bool):
                value3_type = 'bool'
            if isinstance(value3, str) and value3 != '\00nil':
                value3_type = 'string'
            if value3 == '\00nil':
                value3_type = 'nil'
            if value2_type != value3_type and value2_type != 'nil' and value3_type != 'nil':
                exit(53)

            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'JUMPIFEQ':
                if value2 == value3:
                    instruction = instructions_array_sorted.index(int(label_dic[arg_arg])) - 1
            if instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'JUMPIFNEQ':
                if value2 != value3:
                    instruction = instructions_array_sorted.index(int(label_dic[arg_arg])) - 1

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'BREAK':
            stderrDebug(instructions_array[instructions_array_sorted[instruction]]['order'], instruction + 1, GF_dic, LF_stack, TF_dic, is_tf_init, call_stack, label_dic, data_stack)

        elif instructions_array[instructions_array_sorted[instruction]]['opcode'].upper() == 'LABEL':
            pass #labely jsou vytvoreny jiz v predchozim pruchodu ve funkci XMLsyntaxAndLabelCheck

        else:
            exit(32)
        instruction += 1

    if input_file['input'] != None:
        input_open_file.close()

    if is_output:
        print(write_output, end='')

    if dbg:
        debug(instructions_array, GF_dic, LF_stack, TF_dic, is_tf_init, call_stack, label_dic, data_stack)

    exit(exit_value)

#
# Debugujici funkce ukazujici stavy jednotlivych framu.
#
def debug(instruction_array, GF_dic, LF_stack, TF_dic, is_tf_init, call_stack, label_dic, data_stack):
    print('-------------------------------------------------------')
    print('--- FRAMES ---')
    print('GLOBAL FRAME: ', end='')
    print(GF_dic)
    print('LOCAL FRAME: ', end='')
    print(LF_stack, end='')
    print(' <- TOP')
    if is_tf_init == True:
        print('TEMPORARY FRAME: ', end='')
        print(TF_dic)
    else:
        print('TEMPORARY FRAME: None')
    print('')
    print('--- CALLS ---')
    print('CALL STACK: ', end='')
    print(call_stack, end='')
    print(' <- TOP')
    print('LABELS: ', end='')
    print(label_dic)
    print('')
    print('--- DATA ---')
    print('DATA STACK: ', end='')
    print(data_stack, end='')
    print(' <- TOP')
    print('')
    print('--- CODE ---')
    for instruction in instruction_array:
        print(instruction_array[instruction])

# Volani hlavni funkce programu.
doInstructions(False)