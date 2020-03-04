import magma as m
from pathlib import Path
from tapdance.jtag_drv import JTAGLowLevelDriver

def test_tap(width=5):
    # declare circuit
    dut = m.define_from_verilog_file("verilog/dut.v")[0]

    # instantiate tester
    t = JTAGLowLevelDriver(dut, width=width)

    # reset the driver
    t.reset()

    # read ID
    id_val = t.read_id()

    # run simulation
    DW_tap_v = Path(__file__).resolve().parent.parent / 'noupload' / 'DW_tap.v'
    dut_v = Path(__file__).resolve().parent / 'verilog' / 'dut.v'
    t.compile_and_run(
        target='system-verilog',
        simulator='iverilog',
        ext_libs=[DW_tap_v, dut_v],
        ext_model_file=True
    )

    # print ID
    print('JTAG ID:')
    print('{0:0{1}x}'.format(id_val.value, 8))

if __name__ == '__main__':
    test_tap()
