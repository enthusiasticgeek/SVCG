// jkff.v  JK flip-flop with async active-low preset and clear
module JKFF (
    input  wire J,
    input  wire CLK,
    input  wire K,
    input  wire PRE,
    input  wire CLR,
    output reg  Q,
    output wire Q_bar
);
    always @(posedge CLK or negedge PRE or negedge CLR) begin
        if (!PRE)
            Q <= 1'b1;
        else if (!CLR)
            Q <= 1'b0;
        else
            case ({J, K})
                2'b00: Q <= Q;
                2'b01: Q <= 1'b0;
                2'b10: Q <= 1'b1;
                2'b11: Q <= ~Q;
            endcase
    end
    assign Q_bar = ~Q;
endmodule
