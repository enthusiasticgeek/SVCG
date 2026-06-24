// tristatebuf_8.v  8-channel tri-state buffer
module TristateBuffer8 (
    input  wire I0,
    input  wire I1,
    input  wire I2,
    input  wire I3,
    input  wire I4,
    input  wire I5,
    input  wire I6,
    input  wire I7,
    input  wire EN,
    output wire O0,
    output wire O1,
    output wire O2,
    output wire O3,
    output wire O4,
    output wire O5,
    output wire O6,
    output wire O7
);
    assign O0 = EN ? I0 : 1'bz;
    assign O1 = EN ? I1 : 1'bz;
    assign O2 = EN ? I2 : 1'bz;
    assign O3 = EN ? I3 : 1'bz;
    assign O4 = EN ? I4 : 1'bz;
    assign O5 = EN ? I5 : 1'bz;
    assign O6 = EN ? I6 : 1'bz;
    assign O7 = EN ? I7 : 1'bz;
endmodule
