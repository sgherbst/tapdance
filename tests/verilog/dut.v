module dut(
    input tck,
    input trst_n,
    input tms,
    input tdi,
    output tdo
);
    DW_tap #(
        .width(5),
        .id(1),
        .version('hc),
        .part('hafe),
        .man_num('hf00d),
        .sync_mode(1)
    ) DW_tap_i (
        // inputs
        .tck(tck),
        .trst_n(trst_n),
        .tms(tms),
        .tdi(tdi),
        .so(0),
        .bypass_sel(0),
        .sentinel_val(0),
        .test(0),
        // outputs
        .clock_dr(),
        .shift_dr(),
        .update_dr(),
        .tdo(tdo),
        .tdo_en(),
        .tap_state(),
        .extest(),
        .samp_load(),
        .instructions()
    );
endmodule