// ha.v  Half Adder
module HA (
    input  wire A,
    input  wire B,
    output wire SO,
    output wire CO
);
    assign SO = A ^ B;
    assign CO = A & B;
endmodule
