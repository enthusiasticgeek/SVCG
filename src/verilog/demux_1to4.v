// demux_1to4.v  1-to-4 demultiplexer with enable
module DEMUX_1TO4 (
    input  wire I,
    input  wire S0,
    input  wire S1,
    input  wire EN,
    output reg  O0,
    output reg  O1,
    output reg  O2,
    output reg  O3
);
    always @(*) begin
        O0 = 1'b0; O1 = 1'b0; O2 = 1'b0; O3 = 1'b0;
        if (EN)
            case ({S1, S0})
                2'b00: O0 = I;
                2'b01: O1 = I;
                2'b10: O2 = I;
                2'b11: O3 = I;
            endcase
    end
endmodule
