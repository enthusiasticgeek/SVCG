// srff.v  SR flip-flop with async active-low preset and clear
module SRFF (
    input  wire S,
    input  wire CLK,
    input  wire R,
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
        else if (S && !R)
            Q <= 1'b1;
        else if (!S && R)
            Q <= 1'b0;
        // S=1,R=1 is forbidden; S=0,R=0 holds
    end
    assign Q_bar = ~Q;
endmodule
