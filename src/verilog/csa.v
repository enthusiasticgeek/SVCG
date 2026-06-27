// csa.v  (1-bit carry save adder / 3:2 compressor)
// Reduces three addend bits to a sum bit SO and carry bit CO without
// propagating the carry to the next bit position.
module CSA (
    input  wire A, B, C,
    output wire SO,
    output wire CO
);
    assign SO = A ^ B ^ C;
    assign CO = (A & B) | (A & C) | (B & C);
endmodule
