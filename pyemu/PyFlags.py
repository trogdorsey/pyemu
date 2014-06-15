#!/usr/bin/env python

########################################################################
#
# PyEmu: scriptable x86 emulator
#
# Cody Pierce - cpierce@tippingpoint.com - 2007
#
# License: None
#
########################################################################

'''
    This is a new class for setting flags.  It is used by PyCPU to set
    flags per instruction.  This was shamelessly ripped from Bochs

    http://bochs.sourceforge.net/
'''

class PyFlags(object):
    parity_lookup_table = [1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1,
                           0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0,
                           0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0,
                           1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1,
                           0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0,
                           1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1,
                           1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1,
                           0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0,
                           0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0,
                           1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1,
                           1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1,
                           0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0,
                           1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1,
                           0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0,
                           0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0,
                           1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1]

    def __init__(self, mnemonic, op1, op2, result, size):
        assert isinstance(mnemonic, str)
        assert isinstance(op1, long) or isinstance(op1, int)
        assert isinstance(op2, long) or isinstance(op2, int)
        assert isinstance(result, long) or isinstance(result, int)
        assert isinstance(size, long) or isinstance(size, int)

        self.mnemonic = mnemonic
        self.op1 = op1
        self.op2 = op2
        self.result = result
        self.size = size
        self.bit_count = self.size * 8
        self.mask = (2 ** (self.bit_count) - 1)
        self.sign_mask = (self.mask + 1) / 2

    def get_CF(self):
        if self.mnemonic == "ADD":
            carry_flag = int(self.result < self.op1)
        elif self.mnemonic == "ADC":
            # used only if CF = 1
            carry_flag = int(self.result <= self.op1)
        elif self.mnemonic in ["SUB", "CMP"]:
            carry_flag = int(self.op1 < self.op2)
        elif self.mnemonic == "SBB":
            # used only if CF = 1
            carry_flag = int((self.op1 < self.result) or (self.op2 == self.mask))
        elif self.mnemonic == "NEG":
            carry_flag = int(self.result != 0)
        elif self.mnemonic == "LOGIC":
            carry_flag = 0
        elif self.mnemonic == "SAR":
            if self.op2 < self.bit_count:
                carry_flag = int((self.op1 >> (self.op2 - 1)) & 0x01)
            else:
                carry_flag = int((self.op1 & self.sign_mask) > 0)
        elif self.mnemonic in ["SHR", "SHRD"]:
            carry_flag = int((self.op1 >> (self.op2 - 1)) & 0x01)
        elif self.mnemonic in ["SHL", "SAL"]:
            if self.op2 <= self.bit_count:
                carry_flag = int((self.op1 >> (self.bit_count - self.op2)) & 0x01)
            else:
                carry_flag = 0
        elif self.mnemonic == "IMUL":
            carry_flag = int(not ((self.op1 < self.sign_mask and self.op2 == 0) or ((self.op1 & self.sign_mask) and self.op2 == self.mask)))

        elif self.mnemonic == "MUL":
            carry_flag = int(self.op2 != 0)
        else:
            carry_flag = None

        return carry_flag

    def get_AF(self):
        if self.mnemonic in ["ADD", "ADC", "SUB", "CMP", "SBB"]:
            adjust_flag = int(((self.op1 ^ self.op2) ^ self.result) & 0x10)
        elif self.mnemonic == "NEG":
            adjust_flag = int((self.result & 0x0f) != 0)
        elif self.mnemonic == "INC":
            adjust_flag = int((self.result & 0x0f) == 0)
        elif self.mnemonic == "DEC":
            adjust_flag = int((self.result & 0x0f) == 0x0f)
        else:
            adjust_flag = None

        return adjust_flag

    def get_ZF(self):
        if self.mnemonic in ["LOGIC", "ADD", "ADC", "SUB", "CMP", "SBB", "NEG", "SAR", "SHR", "SHL", "SAR", "INC", "DEC"]:
            zero_flag = int(self.result == 0)
        elif self.mnemonic in ["IMUL", "MUL"]:
            zero_flag = int(self.op1 == 0)
        else:
            zero_flag = None

        return zero_flag

    def get_SF(self):
        if self.mnemonic in ["LOGIC", "ADD", "ADC", "SUB", "CMP", "SBB", "NEG", "SAR", "SHR", "SHL", "SAL", "INC", "DEC"]:
            sign_flag = int(self.result >= self.sign_mask)
        elif self.mnemonic in ["IMUL", "MUL"]:
            sign_flag = int(self.op1 >= self.sign_mask)
        else:
            sign_flag = None

        return sign_flag

    def get_OF_ADD(self):
        return int(((~((self.op1) ^ (self.op2)) & ((self.op2) ^ (self.result))) & (self.sign_mask)) != 0)

    def get_OF_SUB(self):
        return int(((((self.op1) ^ (self.op2)) & ((self.op1) ^ (self.result))) & (self.sign_mask)) != 0)

    def get_OF(self):
        if self.mnemonic in ["ADD", "ADC"]:
            overflow_flag = self.get_OF_ADD()
        elif self.mnemonic in ["SUB", "CMP", "SBB"]:
            overflow_flag = self.get_OF_SUB()
        elif self.mnemonic == "NEG":
            overflow_flag = int(self.result == self.sign_mask)
        elif self.mnemonic in ["LOGIC", "SAR"]:
            overflow_flag = 0
        elif self.mnemonic == "SHR":
            if self.op2 == 1:
                overflow_flag = int(self.op1 >= self.sign_mask)
            else:
                overflow_flag = 0
        elif self.mnemonic == "SHRD":
            overflow_flag = int((((self.result << 1) ^ self.result) & self.sign_mask) > 0)
        elif self.mnemonic in ["SHL", "SAL"]:
            if self.op2 == 1:
                overflow_flag = int(((self.op1 ^ self.result) & self.sign_mask) > 0)
            else:
                overflow_flag = int((((self.op1 << (self.op2 - 1)) ^ self.result) & self.sign_mask) > 0)
        elif self.mnemonic == "IMUL":
            overflow_flag = int(not ((self.op1 < self.sign_mask and self.op2 == 0) or ((self.op1 & self.sign_mask) and self.op2 == self.mask)))
        elif self.mnemonic == "MUL":
            overflow_flag = int(self.op2 != 0)
        elif self.mnemonic == "INC":
            overflow_flag = int(self.result == self.sign_mask)
        elif self.mnemonic == "DEC":
            overflow_flag = int(self.result == self.sign_mask - 1)
        else:
            overflow_flag = None

        return overflow_flag

    def get_PF(self):
        if self.mnemonic in ["LOGIC", "ADD", "ADC", "SUB", "CMP", "SBB", "NEG", "SAR", "SHR", "SHL", "SAR", "INC", "DEC"]:
            parity_flag = self.parity_lookup_table[self.result & 0xff]
        elif self.mnemonic in ["IMUL", "MUL"]:
            parity_flag = self.parity_lookup_table[self.op1 & 0xff]
        else:
            parity_flag = None

        return parity_flag


# End PyFlags
