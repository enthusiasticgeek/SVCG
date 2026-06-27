// carry_sel4.v  (4-bit carry select adder)
// Splits into two 2-bit halves; high half computed twice (CIN=0 and CIN=1)
// and muxed once the low carry is resolved.
module CARRY_SEL4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    input  wire CIN,
    output wire S0, S1, S2, S3,
    output wire COUT
);
    // Low half (bits 0-1)
    wire s0_lo = A0 ^ B0 ^ CIN;
    wire c1_lo = (A0 & B0) | (A0 & CIN) | (B0 & CIN);
    wire s1_lo = A1 ^ B1 ^ c1_lo;
    wire c2_lo = (A1 & B1) | (A1 & c1_lo) | (B1 & c1_lo);

    // High half assuming CIN=0
    wire s2_h0 = A2 ^ B2;
    wire c3_h0 = A2 & B2;
    wire s3_h0 = A3 ^ B3 ^ c3_h0;
    wire c4_h0 = (A3 & B3) | (A3 & c3_h0) | (B3 & c3_h0);

    // High half assuming CIN=1
    wire s2_h1 = A2 ^ B2 ^ 1'b1;
    wire c3_h1 = (A2 & B2) | A2 | B2;
    wire s3_h1 = A3 ^ B3 ^ c3_h1;
    wire c4_h1 = (A3 & B3) | (A3 & c3_h1) | (B3 & c3_h1);

    assign S0   = s0_lo;
    assign S1   = s1_lo;
    assign S2   = c2_lo ? s2_h1 : s2_h0;
    assign S3   = c2_lo ? s3_h1 : s3_h0;
    assign COUT = c2_lo ? c4_h1 : c4_h0;
endmodule
