#!/usr/bin/env python3
# OISC:3 parser
 # Copyright (C) 2022 McChuck
 # based on original Copyright (C) 2013 Chris Lloyd
 # Released under GNU General Public License
 # See LICENSE for more details.
 # https://github.com/cjrl
 # lloyd.chris@verizon.net

 #  A B C   [C] = [B] - [A]
 #  A B     [B] = [B] - [A]
 #  A       [A] = [A] - [A]         set A to 0
 #  *A B *C [[C]] = [B] - [[A]]     indirect referencing denoted by float type

 #  A B 0   [B] = [B] - A           A is literal
 #  A 0 C   If [A] <= 0, call C     nextpoint added to return stack
 #  0 B C   If [B] <=0, jump C
 #  A 0 0   push [A] on stack
 #  0 B 0   pop the top of stack to B
 #  0 0 C   Execute instruction [C] on stack
 #  0 0 0   Return                  pops the top of return stack to nextpoint


 #  ?        next address
 #  @        this address
 #  label:   address label, cannot be the only thing on a line
 #  *label   pointer to address label, represented as a floating point number
 #  !        0
 #  ;        end of instruction
 #  #        comment
 #  " or '   string delimeters, must be data
 #  %        data indicator (not needed in negative memory)
 #  % --NEGATIVE: --NEGATIVE--    begin negative memory


class Parser:

    tokens = []
    label_table = {}
    neg0 = 0


    def parse(self,string):
        string = self.expand_literals(string)
        string = string.replace('\n',';')
        string = string.replace('#',';#')
        string = string.replace(':',': ')
        string = string.replace('%','% ')
        string = string.replace('!', "0 ")
        string = string.replace('@', '@ ')
        string = string.replace('?', '? ')
        string = string.replace(',', ' ')
        self.strip_tokens(string)
        self.parse_labels()
        self.handle_macros()
        self.expand_instructions()
        self.update_labels()
        self.tokens = [token for token in sum(self.tokens, []) if token != '%']
        self.neg0 = self.label_table["--NEGATIVE--"]
        self.resolve_negatives()
        self.resolve_labels();

        try:
            response = []
            for token in self.tokens:
                if '.' in str(token):
                    response.append(float(token))
                else:
                    response.append(int(token))
            return(response, self.neg0)
        except ValueError:
            print("Unmatched label:", token, flush=True)
            raise


    def strip_tokens(self, string):
        self.tokens = [token.split() for token in string.split(';') if not '#' in token and token.strip()]
        z_found = False
        for i, token in enumerate(self.tokens):
            if 'ZERO:' in token:
                z_found = True
        if z_found == False:
            self.tokens.append(['ZERO:', '0'])


    def macro_fail(self, instr, token):
        print("Macro", instr, "failed at", token)
        raise ValueError


    def handle_macros(self):                ###############
        for i, token in enumerate(self.tokens):
            instr = token[0]
            if instr[0] == '/':
                self.tokens[i].remove(instr)
                count = len(token)
                if instr == "/sub":
                    if count == 0:
                        self.macro_fail(instr, token)
                elif instr == "/lit-":
                    if count == 2:
                        token.append('0')
                        self.tokens[i] = token
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/call":
                    if count == 1:
                        self.tokens[i].insert(0, 'ZERO')
                        self.tokens[i].insert(1, '0')
                    elif count == 2:
                        self.tokens[i].insert(1, '0')
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/jump":
                    if count == 1:
                        self.tokens[i].insert(0, '0')
                        self.tokens[i].insert(1, 'ZERO')
                    elif count == 2:
                        self.tokens[i].insert(0, '0')
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/push":
                    if count == 1:
                        self.tokens[i].extend(['0', '0'])
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/pop":
                    if count == 1:
                        self.tokens[i].append('0')
                        self.tokens[i].insert(0, '0')
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/exec":
                    if count == 1:
                        self.tokens[i].insert(0, '0')
                        self.tokens[i].insert(1, '0')
                    else:
                        self.macro_fail(instr, token)
                elif instr == "/ret":
                    if count == 0:
                        self.tokens[i] = ['0', '0', '0']
                    else:
                        self.macro_fail(instr, token)
                else:
                    self.macro_fail(instr, token)


    def resolve_negatives(self):
        negmem = False
        maxtoken = len(self.tokens)
        how_many = maxtoken - self.neg0
        reversed_tokens = []
        for i, label in enumerate(self.label_table):
            value = self.label_table[label]
            if label == "--NEGATIVE--":
                negmem = True
            elif negmem == True:
                self.label_table[label] = self.neg0 - value
        for i in range(how_many):
            item = self.tokens.pop(-1)
            reversed_tokens.append(item)
        reversed_tokens.pop(-1)
        self.tokens.extend(reversed_tokens)


    def resolve_labels(self):
        for i, token in enumerate(self.tokens):
            if token[0] == "*":                 # pointer
                token = token[1:]
                if token in self.label_table:
                    self.tokens[i] = float(self.label_table[token])
            else:
                if token in self.label_table:
                    self.tokens[i] = self.label_table[token]
                elif token == '?':
                    if i < self.neg0:
                        self.tokens[i] = i+1
                    else:
                        self.tokens[i] = i - len(self.tokens) - 1
                elif token == '@':
                    if i < self.neg0:
                        self.tokens[i] = i
                    else:
                        self.tokens[i] = i - len(self.tokens)


    def update_labels(self):
        for i, label in enumerate(self.label_table):
            self.label_table[label] = self.get_label_index(label)


    def get_label_index(self,label):
        index = 0
        address, x = self.label_table[label]
        for i in range(address):
            index += len(self.tokens[i])
            if '%' in self.tokens[i][0]:
                index -= 1 
        if '%' in self.tokens[address][0]:
            return index + x - 1
        return index


    def expand_instructions(self):
        pastneg = False
        for token_index, token in enumerate(self.tokens):
            if "--NEGATIVE--" in token:
                pastneg = True
            if not(token[0] == '%' or pastneg == True):
                how_many = len(token)
                if how_many == 1:
                    oprands = [token[0], token[0], token[0]]
                elif how_many == 2:
                    oprands = [token[0], token[1], token[1]]
                elif how_many == 3:
                    oprands = [token[0], token[1], token[2]]
                else:
                    print("Too many tokens", token)
                for i, oprand in enumerate(token):
                    oprands[i] = oprand
                self.tokens[token_index] = oprands


    def parse_labels(self):
        for token_index, token in enumerate(self.tokens):
            for operand_index, operand in enumerate(token):
                if operand[-1] == ':':                                         # ':' in operand:
                    token.remove(operand)
                    operand = operand[:-1]
                    self.label_table[operand] = (token_index, operand_index)


    def expand_literals(self,string):
        in_dq_literal = False       # "
        in_sq_literal = False       # '
        expanded_string = ""
        for char in string:
            if char == '"' and not in_sq_literal:
                in_dq_literal ^= True
            elif char == "'" and not in_dq_literal:
                in_sq_literal ^= True
            elif in_dq_literal or in_sq_literal:
                expanded_string += str(ord(char)) + ' '
            else:
                expanded_string += char
        return expanded_string
