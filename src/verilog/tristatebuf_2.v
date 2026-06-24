// tristatebuf_2.v  2-channel tri-state buffer
module TristateBuffer (
    input  wire I0,
    input  wire I1,
    input  wire EN,
    output wire O0,
    output wire O1
);
    assign O0 = EN ? I0 : 1'bz;
    assign O1 = EN ? I1 : 1'bz;
endmodule
