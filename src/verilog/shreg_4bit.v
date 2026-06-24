// shreg_4bit.v  4-bit serial-in parallel-out shift register
module SHREG_4BIT (
    input  wire SIN,
    input  wire CLK,
    input  wire RST,
    output wire Q0,
    output wire Q1,
    output wire Q2,
    output wire Q3
);
    reg [3:0] reg_q;
    always @(posedge CLK or posedge RST) begin
        if (RST)
            reg_q <= 4'b0000;
        else
            reg_q <= {reg_q[2:0], SIN};
    end
    assign Q0 = reg_q[0];
    assign Q1 = reg_q[1];
    assign Q2 = reg_q[2];
    assign Q3 = reg_q[3];
endmodule
