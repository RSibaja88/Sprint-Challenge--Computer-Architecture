"""CPU functionality."""
#CPU Central Processing Unit. Also called a processor.
# The CPU performs basic arithmetic, logic, controlling, and input/output (I/O) operations specified by the instructions in the program

import sys

# MAIN OPCODES
LDI = 0b10000010
HLT = 0b00000001
PRN = 0b01000111
MUL = 0b10100010
NOP = 0b00000000
POP = 0b01000110
RET = 0b00010001
CALL = 0b01010000
PUSH = 0b01000101
SP = 0b00000111
ADD = 0b10100000
SUB = 0b10100001
CMP = 0b10100111 #compares values and flags
EQ = 0b00000111
JMP = 0b01010100 # Jumps PC to an address in spec. register
JEQ = 0b01010101 # If E flag is set to true, 1, jump to that register
JNE = 0b01010110 # If E flag is cleared to false, 0, it jumps there

# BITWISE ALU OPCODES - (stretch)
# In computer programming, a bitwise operation operates on a bit string, a bit array or a binary numeral (considered as a bit string) at the level of its individual bits. It is a fast and simple action, basic to the higher level arithmetic operations and directly supported by the processor. Most bitwise operations are presented as two-operand instructions where the result replaces one of the input operands.

AND = 0b10101000 # AND is a binary operation that takes two equal-length binary representations and performs the logical AND operation on each pair of the corresponding bits. like Mult
MOD = 0b10100100
SHL = 0b10101100
SHR = 0b10101101
XOR = 0b10101011 #A bitwise XOR is a binary operation that takes two bit patterns of equal length and performs the logical exclusive OR operation on each pair of corresponding bits. The result in each      position is 1 if only one of the bits is 1, but will be 0 if both are 0 or both are 1.

OR = 0b10101010 # A bitwise OR is a binary operation that takes two bit patterns of equal length and performs the logical inclusive OR operation on each pair of corresponding bits. 0 or 1 are the results.
NOT = 0b01101001


class CPU:
    """Main CPU class."""
        #Create new CPU
    def __init__(self):
        self.reg = [0] * 8
        #initalizing 8 registers
        self.ram = [0] * 256
        #initalizing memory
        self.flag_reg = [0] * 8
        # initizlizing flags. the flags register holds the current flags status. These flags can change based on different operands.
        #In computer science, a flag is a value that acts as a signal for a function or process. The value of the flag is used to determine the next step of a program. Flags are often binary flags, which contain a boolean value (true or false).
        self.pc = 0
        # program counter
        self.running = True
        # keeps it running until halted
        # setting up branch table
        self.branch_table = {
            NOP: self.NOP, # no operation
            HLT: self.HLT, # halt
            PRN: self.PRN, # print
            LDI: self.LDI, # load read data from mem to reg, LDI is indirect mode
            MUL: self.MUL, # multiply
            ADD: self.ADD, # addition
            SUB: self.SUB, # subtract
            PUSH: self.PUSH, # inserting one operand at the top of the stack and it decrease the stack pointer register.
            POP: self.POP, # deleting one operand from the top of the stack and it increase the stack pointer register.
            CALL: self.CALL, # call instruction clearly transfers control to another procedure
            RET: self.RET, # returns to the instruction following the call.
            CMP: self.CMP, # compares values and flags
            JMP: self.JMP, # Jumps PC to an address in spec. register
            JEQ: self.JEQ, # If E flag is set to true, 1, jump to that register
            JNE: self.JNE # If E flag is cleared to false, 0, it jumps there
        }

#  A branch table or jump table is a method of transferring program control (branching) to another part of a program.
# A branch table consists of a serial list of unconditional branch instructions that is branched into using an offset created by multiplying a sequential index by the instruction length (the number of bytes in memory occupied by each branch instruction).
# Another method of implementing a branch table is with an array of pointers from which the required function's address is retrieved. This method is also more recently known under such different names as "dispatch table" or "virtual method table" but essentially performing exactly the same purpose.

    def load(self):
        # Load program into memory
        filename = sys.argv[1]
        address = 0

        with open(filename) as f:
            for line in f:
                line = line.split('#')[0].strip() # linesplit at the # and strips the whitespace
                if line == '':
                    continue
                try:
                    v = int(line, 2)
                except ValueError:
                    continue
                self.ram_write(address, v)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        #arithmetic logic unit

        if op == "ADD": #addition
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL": #multiplication
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "SUB": #subtraction
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "CMP": #compares
            if reg_a == reg_b:
                self.flag_reg[EQ] = 0b00000001
            else:
                self.flag_reg[EQ] = 0b00000000
        elif op == "AND": # bitwise AND, equivalent to multiplying them.
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]
        elif op == "MOD":
            if self.reg[reg_b] == 0:
                print("Cannot mod by value of 0")
                self.HLT(reg_a, reg_b)
            else:
                self.reg[reg_a] %= self.reg[reg_b]
        elif op == "SHL":
            self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >> self.reg[reg_b]
        elif op == "OR": # kinda like a boolean, only 0 or 1 can be result
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] -= 0b11111111
        elif op == "XOR":
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        #function to print out the CPU state. You would call this from run() if you need help debugging.

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def LDI(self, reg_a, reg_b):
        self.reg[reg_a] = reg_b

    def HLT(self, reg_a, reg_b):
        self.running = False
        #halting
    def PRN(self, reg_a, reg_b):
        print(self.reg[reg_a])

    def MUL(self, reg_a, reg_b):
        self.alu("MUL", reg_a, reg_b)

    def SUB(self, reg_a, reg_b):
        self.alu("SUB", reg_a, reg_b)

    def ADD(self, reg_a, reg_b):
        self.alu("ADD", reg_a, reg_b)

    def NOP(self, reg_a, reg_b):
        pass

    def PUSH(self, reg_a, reg_b):
        reg_num = self.ram[reg_a]
        value = self.reg[reg_num]
        self.reg[SP] -= 1
        top_of_stack_add = self.reg[SP]
        self.ram[top_of_stack_add] = value

    def POP(self, reg_a, reg_b):
        top_of_stack_add = self.reg[SP]
        value = self.ram[top_of_stack_add]
        reg_num = self.ram[reg_a]
        self.reg[reg_num] = value
        self.reg[SP] += 1

    def CALL(self, reg_a, reg_b):
        return_addr = reg_b

        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = return_addr

        reg_num = self.ram[reg_a]
        subroutine_addr = self.reg[reg_num]

        self.pc = subroutine_addr

    def RET(self, reg_a, reg_b):
        subroutine_addr = self.ram[self.reg[SP]]
        self.reg[SP] += 1
        self.pc = subroutine_addr

    def CMP(self, reg_a, reg_b):
        reg_num1 = self.reg[reg_a]
        reg_num2 = self.reg[reg_b]
        self.alu("CMP", reg_num1, reg_num2)

    def JMP(self, reg_a, reg_b):
        self.pc = self.reg[reg_a]

    def JEQ(self, reg_a, reg_b):
        if self.flag_reg[EQ] == 0b00000001:
            self.pc = self.reg[reg_a]
        else:
            self.pc += 2

    def JNE(self, reg_a, reg_b):
        if self.flag_reg[EQ] == 0b00000000:
            self.pc = self.reg[reg_a]
        else:
            self.pc += 2

    def run(self):
        while self.running:
            ir = self.ram_read(self.pc)
            pc_flag = (ir & 0b00010000) >> 4
            reg_num1 = self.ram[self.pc + 1]
            reg_num2 = self.ram[self.pc + 2]
            self.branch_table[ir](reg_num1, reg_num2)
            if pc_flag == 0:
                move = int((ir & 0b11000000) >> 6)
                self.pc += move + 1

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value
