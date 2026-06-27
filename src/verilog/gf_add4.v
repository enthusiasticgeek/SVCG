// gf_add4.v  (4-bit GF(2^4) adder)
// Addition in GF(2^m) is bitwise XOR; no carry exists.
module GF_ADD4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    output wire R0, R1, R2, R3
);
    assign R0 = A0 ^ B0;
    assign R1 = A1 ^ B1;
    assign R2 = A2 ^ B2;
    assign R3 = A3 ^ B3;
endmodule
