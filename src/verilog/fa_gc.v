// fa_gc.v  Full Adder Gray Cell (Kogge-Stone / parallel prefix)
module FA_GC (
    input  wire A,
    input  wire B,
    input  wire SI,
    input  wire CI,
    output wire SO,
    output wire CO
);
    wire G, P;
    assign G  = A & B;
    assign P  = A ^ B;
    assign CO = G | (P & SI);
    assign SO = P ^ CI;
endmodule
