// fa.v  Full Adder
module FA (
    input  wire A,
    input  wire B,
    input  wire SI,
    input  wire CI,
    output wire SO,
    output wire CO
);
    assign SO = A ^ B ^ SI;
    assign CO = (A & B) | (SI & (A ^ B));
endmodule
