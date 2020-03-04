import magma as m
from pathlib import Path
from tapdance.jtag_drv import JTAGLowLevelDriver

def test_tap(width=5):
    # declare circuit
    class DW_tap(m.Circuit):
        io = m.IO(
            # inputs
            tck=m.BitIn,
            trst_n=m.BitIn,
            tms=m.BitIn,
            tdi=m.BitIn,
            so=m.BitIn,
            bypass_sel=m.BitIn,
            sentinel_val=m.In(m.Bits[width-1]),
            test=m.BitIn,
            # outputs
            clock_dr=m.BitOut,
            shift_dr=m.BitOut,
            update_dr=m.BitOut,
            tdo=m.BitOut,
            tdo_en=m.BitOut,
            tap_state=m.Out(m.Bits[16]),
            extest=m.BitOut,
            samp_load=m.BitOut,
            instructions=m.Out(m.Bits[width])
        )

    # specify parameters of the circuit
    parameters = {
        'width': width,
        'id': 1,
        'version': 0xc,
        'part': 0xafe,
        'man_num': 0xf00d >> 1,
        'sync_mode': 1
    }

    # instantiate tester
    t = JTAGLowLevelDriver(DW_tap, width=width)

    # initialize custom signals
    t.poke(DW_tap.so, 0)
    t.poke(DW_tap.bypass_sel, 0)
    t.poke(DW_tap.sentinel_val, 0)
    t.poke(DW_tap.test, 0)
    t.eval()

    # reset the driver
    t.reset()

    # read ID
    id_val = t.read_id()

    # run simulation
    DW_tap_v = Path(__file__).resolve().parent.parent / 'noupload' / 'DW_tap.v'
    t.compile_and_run(
        target='system-verilog',
        simulator='iverilog',
        ext_libs=[DW_tap_v],
        parameters=parameters,
        ext_model_file=True
    )

    # print ID
    print('JTAG ID:')
    print('{0:0{1}x}'.format(id_val.value, 8))

if __name__ == '__main__':
    test_tap()
