// dec_2to4.v  2-to-4 decoder with enable
module DEC_2TO4 (
    input  wire A,
    input  wire B,
    input  wire EN,
    output wire Y0,
    output wire Y1,
    output wire Y2,
    output wire Y3
);
    assign Y0 = EN & ~A & ~B;
    assign Y1 = EN & ~A &  B;
    assign Y2 = EN &  A & ~B;
    assign Y3 = EN &  A &  B;
endmodule
