// mod_mul4.v  (4-bit modular multiplier)
// R = (A * B) mod M  — 4-bit unsigned operands.
module MOD_MUL4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    input  wire M0, M1, M2, M3,
    output wire R0, R1, R2, R3
);
    reg [7:0] P_v, R_v;
    wire [3:0] A_v = {A3,A2,A1,A0};
    wire [3:0] B_v = {B3,B2,B1,B0};
    wire [3:0] M_v = {M3,M2,M1,M0};

    always @(*) begin
        P_v = A_v * B_v;
        if (M_v == 0) begin
            R_v = P_v;
        end else begin
            R_v = P_v % {4'b0, M_v};
        end
    end

    assign {R3,R2,R1,R0} = R_v[3:0];
endmodule
