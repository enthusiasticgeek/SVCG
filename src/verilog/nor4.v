// nor4.v
module NOR4_GATE (
    input  wire IN1,
    input  wire IN2,
    input  wire IN3,
    input  wire IN4,
    output wire OUT1
);
    assign OUT1 = ~(IN1 | IN2 | IN3 | IN4);
endmodule
