// mux_4x1.v  4:1 multiplexer with enable (EN=0 → high-Z)
module MUX4x1 (
    input  wire I0,
    input  wire I1,
    input  wire I2,
    input  wire I3,
    input  wire S0,
    input  wire S1,
    input  wire EN,
    output reg  O0
);
    always @(*) begin
        if (!EN)
            O0 = 1'bz;
        else
            case ({S1, S0})
                2'b00: O0 = I0;
                2'b01: O0 = I1;
                2'b10: O0 = I2;
                2'b11: O0 = I3;
            endcase
    end
endmodule
