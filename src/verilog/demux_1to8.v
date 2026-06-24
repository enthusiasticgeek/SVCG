// demux_1to8.v  1-to-8 demultiplexer with enable
module DEMUX_1TO8 (
    input  wire I,
    input  wire S0,
    input  wire S1,
    input  wire S2,
    input  wire EN,
    output reg  O0,
    output reg  O1,
    output reg  O2,
    output reg  O3,
    output reg  O4,
    output reg  O5,
    output reg  O6,
    output reg  O7
);
    always @(*) begin
        O0=1'b0; O1=1'b0; O2=1'b0; O3=1'b0;
        O4=1'b0; O5=1'b0; O6=1'b0; O7=1'b0;
        if (EN)
            case ({S2, S1, S0})
                3'b000: O0 = I;
                3'b001: O1 = I;
                3'b010: O2 = I;
                3'b011: O3 = I;
                3'b100: O4 = I;
                3'b101: O5 = I;
                3'b110: O6 = I;
                3'b111: O7 = I;
            endcase
    end
endmodule
