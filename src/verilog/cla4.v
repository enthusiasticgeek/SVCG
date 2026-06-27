// cla4.v  (4-bit carry lookahead adder)
// Parallel carry generation eliminates ripple delay.
module CLA4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    input  wire CIN,
    output wire S0, S1, S2, S3,
    output wire COUT
);
    wire g0 = A0 & B0;
    wire g1 = A1 & B1;
    wire g2 = A2 & B2;
    wire g3 = A3 & B3;
    wire p0 = A0 ^ B0;
    wire p1 = A1 ^ B1;
    wire p2 = A2 ^ B2;
    wire p3 = A3 ^ B3;

    wire c1 = g0 | (p0 & CIN);
    wire c2 = g1 | (p1 & g0) | (p1 & p0 & CIN);
    wire c3 = g2 | (p2 & g1) | (p2 & p1 & g0) | (p2 & p1 & p0 & CIN);
    wire c4 = g3 | (p3 & g2) | (p3 & p2 & g1) | (p3 & p2 & p1 & g0)
                 | (p3 & p2 & p1 & p0 & CIN);

    assign S0   = p0 ^ CIN;
    assign S1   = p1 ^ c1;
    assign S2   = p2 ^ c2;
    assign S3   = p3 ^ c3;
    assign COUT = c4;
endmodule
