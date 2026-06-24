// tristatebuf_4.v  4-channel tri-state buffer
module TristateBuffer4 (
    input  wire I0,
    input  wire I1,
    input  wire I2,
    input  wire I3,
    input  wire EN,
    output wire O0,
    output wire O1,
    output wire O2,
    output wire O3
);
    assign O0 = EN ? I0 : 1'bz;
    assign O1 = EN ? I1 : 1'bz;
    assign O2 = EN ? I2 : 1'bz;
    assign O3 = EN ? I3 : 1'bz;
endmodule
