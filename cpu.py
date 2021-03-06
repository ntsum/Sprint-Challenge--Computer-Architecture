"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

SP = 7

# greater gtf == > flag, ltf == < flag, etf == = flag
ltf = 0b100
gtf = 0b010
etf = 0b001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True
        self.flags = 0b00000001
        self.branch_table = {
            HLT: self.HLT_op,
            LDI: self.LDI_op,
            PRN: self.PRN_op,
            ADD: self.ADD_op,
            MUL: self.MUL_op,
            PUSH: self.PUSH_op,
            POP: self.POP_op,
            CALL: self.CALL_op,
            RET: self.RET_op,
            CMP: self.CMP_op,
            JMP: self.JMP_op,
            JEQ: self.JEQ_op,
            JNE: self.JNE_op
        }

    def HLT_op(self, oper_a, oper_b):
        self.running = False

    def LDI_op(self, oper_a, oper_b):  # Register where to write
        self.reg[oper_a] = oper_b  # Value to write
        self.pc += 3

    def PRN_op(self, oper_a, oper_b):
        print(self.reg[oper_a])
        self.pc += 2

    def ADD_op(self, oper_a, oper_b):
        self.alu('ADD', oper_a, oper_b)
        self.pc += 3

    def MUL_op(self, oper_a, oper_b):
        self.alu('MUL', oper_a, oper_b)
        self.pc += 3

    def PUSH_op(self, oper_a, oper_b):  # Register whose value is to be pushed on stack
        self.push(self.reg[oper_a])
        self.pc += 2

    def POP_op(self, oper_a, oper_b):  # Register in which stack value is to be popped
        self.reg[oper_a] = self.pop()
        self.pc += 2

    def CALL_op(self, oper_a, oper_b):
        self.reg[SP] -= 1  # Register hold PC where to jump
        self.ram[self.reg[SP]] = self.pc + 2
        # Next instruction after CALL. this goes to stack
        update_reg = self.ram[self.pc + 1]
        self.pc = self.reg[update_reg]

    def RET_op(self, oper_a, oper_b):
        self.pc = self.ram[self.reg[SP]]  # Pop from stack the PC
        self.reg[SP] += 1

    def CMP_op(self, oper_a, oper_b):
        self.alu('CMP', oper_a, oper_b)
        self.pc += 3

        # Compare the values in two registers.
        # If they are equal, set the Equal E flag to 1, otherwise set it to 0.
        # If registerA is less than registerB, set the Less-than L flag to 1, otherwise set it to 0.
        # If registerA is greater than registerB, set the Greater-than G flag to 1, otherwise set it to 0.

    def JMP_op(self, oper_a, oper_b):  # Register hold PC where to jump
        self.pc = self.reg[oper_a]  # Jump to instruction pointed in JMP

        # JMP register

        # Jump to the address stored in the given register.
        # Set the PC to the address stored in the given register.

    def JEQ_op(self, oper_a, oper_b):  # Register hold PC where to jump
        if self.flags & etf:  # Jump to instruction pointed in CALL
            self.pc = self.reg[oper_a]
        else:
            self.pc += 2

            # JEQ register
            # If equal flag is set (true), jump to the address stored in the given register.

    def JNE_op(self, oper_a, oper_b):  # Register hold PC where to jump
        if not self.flags & etf:  # Jump to instruction pointed in CALL
            self.pc = self.reg[oper_a]
        else:
            self.pc += 2

            # JNE register
            # If E flag is clear(false, 0), jump to the address stored in the given register.

    def push(self, value):
        self.reg[SP] -= 1
        self.ram_write(value, self.reg[7])

    def pop(self):
        value = self.ram_read(self.reg[7])
        self.reg[SP] += 1
        return value

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""
        address = 0
        with open(sys.argv[1]) as f:
            for line in f:
                # Ignore comments
                comment_split = line.split("#")
                num = comment_split[0].strip()
                if num == "":
                    continue  # Ignore blank lines
                instruction = int(num, 2)  # Base 10, but ls-8 is base 2
                self.ram[address] = instruction
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flags = ltf
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flags = gtf
            else:
                self.flags = etf
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

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

    def run(self):
        """Run the CPU."""
        while self.running:
            IR = self.ram_read(self.pc)
            oper_a = self.ram_read(self.pc + 1)
            oper_b = self.ram_read(self.pc + 2)
            if int(bin(IR), 2) in self.branch_table:
                self.branch_table[IR](oper_a, oper_b)
            else:
                raise Exception(
                    f'Invalid {IR}, not in branch table \t {list(self.branch_table.keys())}')
