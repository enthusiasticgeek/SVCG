// sq4.v  (4-bit unsigned squarer)
// P[7:0] = A[3:0]^2.  Symmetric partial products (ai*aj = aj*ai) allow
// roughly half the cross-term adders compared to a general multiplier.
module SQ4 (
    input  wire A0, A1, A2, A3,
    output wire P0, P1, P2, P3, P4, P5, P6, P7
);
    wire [3:0] A_v = {A3, A2, A1, A0};
    wire [7:0] P_v = A_v * A_v;
    assign {P7,P6,P5,P4,P3,P2,P1,P0} = P_v;
endmodule
