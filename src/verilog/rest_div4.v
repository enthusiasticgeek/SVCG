// rest_div4.v  (4-bit unsigned restoring divider)
// Restoring division: each of 4 steps shifts the partial remainder left,
// trial-subtracts the divisor, and restores if the result is negative.
// Inputs:  N[3:0] dividend, D[3:0] divisor (LSB-first individual bits).
// Outputs: Q[3:0] quotient, R[3:0] remainder (LSB-first).
module REST_DIV4 (
    input  wire N0, N1, N2, N3,
    input  wire D0, D1, D2, D3,
    output wire Q0, Q1, Q2, Q3,
    output wire R0, R1, R2, R3
);
    reg [3:0] Q_v, R_v;
    reg [3:0] N_v, D_v;
    reg [4:0] P, trial;
    integer i;

    always @(*) begin
        N_v = {N3, N2, N1, N0};
        D_v = {D3, D2, D1, D0};
        Q_v = 4'b0;
        P   = 5'b0;
        for (i = 3; i >= 0; i = i - 1) begin
            P     = {P[3:0], N_v[i]};      // shift left, bring in dividend bit
            trial = P - {1'b0, D_v};
            if (trial[4] == 1'b0) begin     // no borrow: P >= D
                Q_v[i] = 1'b1;
                P      = trial;
            end
            // else: restore (keep P unchanged), quotient bit stays 0
        end
        R_v = P[3:0];
    end

    assign {Q3,Q2,Q1,Q0} = Q_v;
    assign {R3,R2,R1,R0} = R_v;
endmodule
