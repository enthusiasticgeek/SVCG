// dec_3to8.v  3-to-8 decoder with enable
module DEC_3TO8 (
    input  wire A,
    input  wire B,
    input  wire C,
    input  wire EN,
    output wire Y0,
    output wire Y1,
    output wire Y2,
    output wire Y3,
    output wire Y4,
    output wire Y5,
    output wire Y6,
    output wire Y7
);
    assign Y0 = EN & ~A & ~B & ~C;
    assign Y1 = EN & ~A & ~B &  C;
    assign Y2 = EN & ~A &  B & ~C;
    assign Y3 = EN & ~A &  B &  C;
    assign Y4 = EN &  A & ~B & ~C;
    assign Y5 = EN &  A & ~B &  C;
    assign Y6 = EN &  A &  B & ~C;
    assign Y7 = EN &  A &  B &  C;
endmodule
