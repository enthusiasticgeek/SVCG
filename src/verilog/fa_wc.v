// fa_wc.v  Full Adder White Cell (Kogge-Stone / parallel prefix)
module FA_WC (
    input  wire A,
    input  wire B,
    input  wire SI,
    input  wire CI,
    output wire SO,
    output wire CO
);
    wire P;
    assign P  = A ^ B;
    assign CO = P & SI;
    assign SO = P ^ CI;
endmodule
