import fault
import magma as m
from pathlib import Path
from tapdance.jtag_drv import JTAGLowLevelDriver

def test_tap(width=5):
    # declare circuit
    dut = m.DeclareCircuit(
        'DW_tap',
        # inputs
        'tck', m.BitIn,
        'trst_n', m.BitIn,
        'tms', m.BitIn,
        'tdi', m.BitIn,
        'so', m.BitIn,
        'bypass_sel', m.BitIn,
        'sentinel_val', m.In(m.Bits[width-1]),
        'test', m.BitIn,
        # outputs
        'clock_dr', m.BitOut,
        'shift_dr', m.BitOut,
        'update_dr', m.BitOut,
        'tdo', m.BitOut,
        'tdo_en', m.BitOut,
        'tap_state', m.Out(m.Bits[16]),
        'extest', m.BitOut,
        'samp_load', m.BitOut,
        'instructions', m.Out(m.Bits[width])
    )
    parameters = {
        'width': width,
        'id': 1,
        'version': (2**4)-1,
        'part': (2**16)-1,
        'man_num': (2**11)-1,
        #'version': 0,
        #'part': 0,
        #'man_num': 0,
        'sync_mode': 1
    }

    # instantiate tester
    t = JTAGLowLevelDriver(dut, width=width)

    # initialize custom signals
    t.poke(dut.so, 0)
    t.poke(dut.bypass_sel, 0)
    t.poke(dut.sentinel_val, 0)
    t.poke(dut.test, 0)
    t.eval()

    # reset the driver
    t.zero()
    t.reset()

    # read ID
    id_val = t.read_id()

    # run simulation
    t.compile_and_run(
        target='system-verilog',
        simulator='iverilog',
        ext_libs=[Path('../ignore/DW_tap.v').resolve()],
        parameters=parameters,
        ext_model_file=True,
        disp_type='realtime'
    )

    # print ID
    #version_vec_cnst[3:0],part_vec_cnst[15:0],
                         #man_num_vec_cnst[10:0],1'b1

    print('{0:0{1}x}'.format(id_val.value,8))

if __name__ == '__main__':
    test_tap()