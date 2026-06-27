// srt_div4.v  (4-bit unsigned SRT radix-2 divider)
// Quotient digit in {-1, 0, +1}; no trial subtract needed.
// digit = +1 if 2P >= D; digit = -1 if 2P <= -D; else digit = 0.
module SRT_DIV4 (
    input  wire N0, N1, N2, N3,
    input  wire D0, D1, D2, D3,
    output wire Q0, Q1, Q2, Q3,
    output wire R0, R1, R2, R3
);
    reg [3:0] N_v, D_v, q_pos, q_neg, Q_v;
    reg signed [5:0] P, D_s, twoP;
    integer i;

    always @(*) begin
        N_v   = {N3, N2, N1, N0};
        D_v   = {D3, D2, D1, D0};
        D_s   = {2'b00, D_v};
        P     = 6'sd0;
        q_pos = 4'b0;
        q_neg = 4'b0;

        for (i = 3; i >= 0; i = i - 1) begin
            P = {P[4:0], N_v[i]};   // shift left, bring in dividend bit
            twoP = P;

            if (twoP >= D_s) begin          // digit = +1
                P        = twoP - D_s;
                q_pos[i] = 1'b1;
            end else if (twoP <= -D_s) begin // digit = -1
                P        = twoP + D_s;
                q_neg[i] = 1'b1;
            end
            // else digit = 0
        end

        Q_v = q_pos - q_neg;

        if (P[5] == 1'b1) begin
            P   = P + D_s;
            Q_v = Q_v - 4'd1;
        end
    end

    assign {Q3,Q2,Q1,Q0} = Q_v;
    assign {R3,R2,R1,R0} = P[3:0];
endmodule
