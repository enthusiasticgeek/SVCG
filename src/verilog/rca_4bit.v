// rca_4bit.v  4-bit ripple carry adder
module RCA_4BIT (
    input  wire A0,
    input  wire A1,
    input  wire A2,
    input  wire A3,
    input  wire B0,
    input  wire B1,
    input  wire B2,
    input  wire B3,
    input  wire CIN,
    output wire S0,
    output wire S1,
    output wire S2,
    output wire S3,
    output wire COUT
);
    wire c1, c2, c3;
    assign S0   = A0 ^ B0 ^ CIN;
    assign c1   = (A0 & B0) | (A0 & CIN) | (B0 & CIN);
    assign S1   = A1 ^ B1 ^ c1;
    assign c2   = (A1 & B1) | (A1 & c1) | (B1 & c1);
    assign S2   = A2 ^ B2 ^ c2;
    assign c3   = (A2 & B2) | (A2 & c2) | (B2 & c2);
    assign S3   = A3 ^ B3 ^ c3;
    assign COUT = (A3 & B3) | (A3 & c3) | (B3 & c3);
endmodule
