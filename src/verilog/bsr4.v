// bsr4.v  (4-bit barrel shifter)
// MODE: 00=logical left, 01=logical right, 1x=arithmetic right
module BSR4 (
    input  wire A0, A1, A2, A3,
    input  wire AMT0, AMT1,
    input  wire MODE0, MODE1,
    output wire R0, R1, R2, R3
);
    reg [3:0] R_v;
    wire [3:0] A_v  = {A3, A2, A1, A0};
    wire [1:0] amt  = {AMT1, AMT0};
    wire [1:0] mode = {MODE1, MODE0};

    always @(*) begin
        case (mode)
            2'b00:   R_v = A_v << amt;                           // logical left
            2'b01:   R_v = A_v >> amt;                           // logical right
            default: R_v = $signed(A_v) >>> amt;                 // arithmetic right
        endcase
    end

    assign {R3, R2, R1, R0} = R_v;
endmodule
