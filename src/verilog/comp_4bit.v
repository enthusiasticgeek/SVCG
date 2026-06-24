// comp_4bit.v  4-bit magnitude comparator
module COMP_4BIT (
    input  wire A0,
    input  wire A1,
    input  wire A2,
    input  wire A3,
    input  wire B0,
    input  wire B1,
    input  wire B2,
    input  wire B3,
    output wire ALB,
    output wire AEB,
    output wire AGB
);
    wire [3:0] A_vec = {A3, A2, A1, A0};
    wire [3:0] B_vec = {B3, B2, B1, B0};
    assign ALB = (A_vec < B_vec) ? 1'b1 : 1'b0;
    assign AEB = (A_vec == B_vec) ? 1'b1 : 1'b0;
    assign AGB = (A_vec > B_vec) ? 1'b1 : 1'b0;
endmodule
