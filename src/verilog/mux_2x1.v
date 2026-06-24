// mux_2x1.v  2:1 multiplexer with enable (EN=0 → high-Z)
module MUX2x1 (
    input  wire I0,
    input  wire I1,
    input  wire S0,
    input  wire EN,
    output wire O0
);
    assign O0 = EN ? (S0 ? I1 : I0) : 1'bz;
endmodule
