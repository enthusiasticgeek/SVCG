// dff_pipeline.v  D flip-flop with synchronous active-low reset (pipeline stage)
module DFF_PIPELINE (
    input  wire D,
    input  wire CLK,
    input  wire N_RST,
    output reg  Q
);
    always @(posedge CLK) begin
        if (!N_RST)
            Q <= 1'b0;
        else
            Q <= D;
    end
endmodule
