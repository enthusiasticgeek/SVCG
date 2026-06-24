// mux_8x1.v  8:1 multiplexer with enable (EN=0 → high-Z)
module MUX8x1 (
    input  wire I0,
    input  wire I1,
    input  wire I2,
    input  wire I3,
    input  wire I4,
    input  wire I5,
    input  wire I6,
    input  wire I7,
    input  wire S0,
    input  wire S1,
    input  wire S2,
    input  wire EN,
    output reg  O0
);
    always @(*) begin
        if (!EN)
            O0 = 1'bz;
        else
            case ({S2, S1, S0})
                3'b000: O0 = I0;
                3'b001: O0 = I1;
                3'b010: O0 = I2;
                3'b011: O0 = I3;
                3'b100: O0 = I4;
                3'b101: O0 = I5;
                3'b110: O0 = I6;
                3'b111: O0 = I7;
            endcase
    end
endmodule
