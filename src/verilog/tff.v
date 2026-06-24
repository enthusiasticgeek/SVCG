// tff.v  T flip-flop with async active-low preset and clear
module TFF (
    input  wire T,
    input  wire CLK,
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
        else if (T)
            Q <= ~Q;
    end
    assign Q_bar = ~Q;
endmodule
