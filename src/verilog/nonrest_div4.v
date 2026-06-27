// nonrest_div4.v  (4-bit unsigned non-restoring divider)
// P>=0: subtract D, digit=+1; P<0: add D, digit=-1.
// Quotient converted from signed-digit {-1,+1} to binary after the loop.
// Post-correction if final partial remainder is negative.
module NONREST_DIV4 (
    input  wire N0, N1, N2, N3,
    input  wire D0, D1, D2, D3,
    output wire Q0, Q1, Q2, Q3,
    output wire R0, R1, R2, R3
);
    reg [3:0] N_v, D_v, qbits, q_pos, q_neg, Q_v, R_v;
    reg signed [5:0] P, D_s;
    integer i;

    always @(*) begin
        N_v = {N3, N2, N1, N0};
        D_v = {D3, D2, D1, D0};
        D_s = {2'b00, D_v};
        P   = 6'sd0;
        qbits = 4'b0;

        for (i = 3; i >= 0; i = i - 1) begin
            P = {P[4:0], N_v[i]};        // shift left, bring in next dividend bit
            if (P[5] == 1'b0) begin      // P >= 0: subtract D
                P        = P - D_s;
                qbits[i] = 1'b1;         // digit = +1
            end else begin               // P < 0: add D (no restore)
                P        = P + D_s;
                qbits[i] = 1'b0;         // digit = -1
            end
        end

        // Convert signed-digit to binary: Q = Q+ - Q-
        q_pos = qbits;
        q_neg = ~qbits;
        Q_v   = q_pos - q_neg;

        // Post-correction
        if (P[5] == 1'b1) begin
            P   = P + D_s;
            Q_v = Q_v - 4'd1;
        end
        R_v = P[3:0];
    end

    assign {Q3,Q2,Q1,Q0} = Q_v;
    assign {R3,R2,R1,R0} = R_v;
endmodule
