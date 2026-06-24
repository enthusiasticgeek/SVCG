// nand.v
module NAND_GATE (
    input  wire IN1,
    input  wire IN2,
    output wire OUT1
);
    assign OUT1 = ~(IN1 & IN2);
endmodule
