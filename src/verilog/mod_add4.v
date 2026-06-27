// mod_add4.v  (4-bit modular adder)
// R = (A + B) mod M.  S = A+B; T = S-M; output T if T>=0, else S.
module MOD_ADD4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    input  wire M0, M1, M2, M3,
    output wire R0, R1, R2, R3
);
    wire [4:0] A_v = {1'b0, A3, A2, A1, A0};
    wire [4:0] B_v = {1'b0, B3, B2, B1, B0};
    wire [4:0] M_v = {1'b0, M3, M2, M1, M0};
    wire [4:0] S_v = A_v + B_v;
    wire [4:0] T_v = S_v - M_v;
    wire [3:0] R_v = T_v[4] ? S_v[3:0] : T_v[3:0];
    assign {R3,R2,R1,R0} = R_v;
endmodule
