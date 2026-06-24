// xor3.v
module XOR3_GATE (
    input  wire IN1,
    input  wire IN2,
    input  wire IN3,
    output wire OUT1
);
    assign OUT1 = IN1 ^ IN2 ^ IN3;
endmodule
