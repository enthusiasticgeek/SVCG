// enc_4to2.v  4-to-2 priority encoder (I3 highest priority)
module ENC_4TO2 (
    input  wire I0,
    input  wire I1,
    input  wire I2,
    input  wire I3,
    output reg  Y0,
    output reg  Y1,
    output reg  VALID
);
    always @(*) begin
        if (I3)      begin Y1 = 1'b1; Y0 = 1'b1; VALID = 1'b1; end
        else if (I2) begin Y1 = 1'b1; Y0 = 1'b0; VALID = 1'b1; end
        else if (I1) begin Y1 = 1'b0; Y0 = 1'b1; VALID = 1'b1; end
        else if (I0) begin Y1 = 1'b0; Y0 = 1'b0; VALID = 1'b1; end
        else         begin Y1 = 1'b0; Y0 = 1'b0; VALID = 1'b0; end
    end
endmodule
