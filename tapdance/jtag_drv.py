import fault
from abc import ABCMeta, abstractmethod

class RegValue:
    def __init__(self, length):
        self.bits = [None] * length
        self.length = length

    def set_bit(self, idx, val):
        self.bits[idx] = val

    @property
    def value(self):
        retval = 0
        for idx in range(self.length):
            retval |= self.bits[idx].value << idx
        return retval

class JTAGLowLevelDriver(fault.Tester, metaclass=ABCMeta):
    def __init__(self, *args, tdi='tdi', tdo='tdo', tck='tck',
                 tms='tms', trst_n='trst_n', svf_file=None,
                 width=5, **kwargs):
        # call super constructor
        super().__init__(*args, **kwargs)

        # save pin mapping settings
        self.tdi = tdi
        self.tdo = tdo
        self.tck = tck
        self.tms = tms
        self.trst_n = trst_n

        # save other settings
        if svf_file is not None:
            self.svf_file = open(svf_file, 'w')
        else:
            self.svf_file = None

        # state variables
        self.reset_done = False
        self.width = width

    def poke_tdi(self, value):
        self.poke(getattr(self._circuit, self.tdi), value)
        self.eval()

    def poke_tms(self, value):
        self.poke(getattr(self._circuit, self.tms), value)
        self.eval()

    def poke_tck(self, value):
        self.poke(getattr(self._circuit, self.tck), value)
        self.eval()

    def poke_trst_n(self, value):
        self.poke(getattr(self._circuit, self.trst_n), value)
        self.eval()

    def get_tdo(self):
        return self.get_value(getattr(self._circuit, self.tdo))

    def cycle(self, num=1):
        for _ in range(num):
            self.poke_tck(1)
            self.poke_tck(0)

    def reset(self):
        # initialize signals
        self.poke_tdi(0)
        self.poke_tck(0)
        self.poke_tms(1)
        self.poke_trst_n(0)
        self.cycle()

        # de-assert reset
        self.poke_trst_n(1)
        self.cycle()

        # go to the IDLE state
        self.poke_tms(1)
        self.cycle(10)  # TODO: investigate if this can be reduced
        self.poke_tms(0)
        self.cycle()

    def svf_write(self, s):
        self.svf_file.write(s)

    def read_id(self):
        self.shift_ir(1, self.width)
        retval = self.shift_dr(0, 32)

        # write SVF command if needed
        if self.svf_file:
            self.svf_write('RUNTEST IDLE 10 TCK IDLE;\n')

        # return deferred-evaluation result
        return retval

    def shift_ir(self, inst_in, length):
        # Move to Select-DR-Scan state
        self.poke_tms(1)
        self.cycle()

        # Move to Select-IR-Scan state
        self.poke_tms(1)
        self.cycle()

        # Move to Capture IR state
        self.poke_tms(0)
        self.cycle()

        # Move to Shift-IR state
        self.poke_tms(0)
        self.cycle()

        # Remain in Shift-IR state and shift in inst_in. Observe the TDO signal to read the x_inst_out
        for i in range(length-1):
            self.poke_tdi((inst_in >> i) & 1)
            self.cycle()

        # Shift in the last bit and switch to Exit1-IR state
        self.poke_tdi((inst_in >> (length - 1)) & 1)
        self.poke_tms(1)
        self.cycle()

        # Move to Update-IR state
        self.poke_tms(1)
        self.cycle()

        # Move to Run-Test/Idle state
        self.poke_tms(0)
        self.cycle(2)

        # Dump SVF if needed
        if self.svf_file:
            mask_len = (length+3)//4
            val_str = f'{0:0{1}x}'.format(inst_in, mask_len)
            mask = 'f' * mask_len
            self.svf_write(f'SIR {length} TDI ({val_str}) SMASK ({mask});\n')

    def shift_dr(self, data_in, length):
        # Move to Select-DR-Scan state
        self.poke_tms(1)
        self.cycle()

        # Move to Capture-DR state
        self.poke_tms(0)
        self.cycle()

        # Move to Shift-DR state
        self.poke_tms(0)
        self.cycle()

        # Remain in Shift-DR state and shift in data_in. Observe the TDO signal to read the data_out
        retval = RegValue(length)
        for i in range(length-1):
            self.poke_tdi((data_in >> i) & 1)
            retval.set_bit(i, self.get_tdo())
            self.cycle()

        # Shift in the last bit and switch to Exit1-DR state
        self.poke_tdi((data_in >> (length - 1)) & 1)
        retval.set_bit(length - 1, self.get_tdo())
        self.poke_tms(1)
        self.cycle()

        # Move to Update-DR state
        self.poke_tms(1)
        self.cycle()

        # Move to Run-Test/Idle state
        self.poke_tms(0)
        self.cycle(2)

        # Dump SVF if needed
        if self.svf_file:
            mask_len = (length+3)//4
            val_str = f'{0:0{1}x}'.format(data_in, mask_len)
            mask = 'f' * mask_len
            self.svf_write(f'SDR {length} TDI ({val_str}) SMASK ({mask});\n')

        # Return deferred evaluation object with the register value
        # Getting the "value" property of this object after simulation
        return retval
