// ks4.v  (4-bit Kogge-Stone parallel prefix adder)
// Two-level parallel prefix tree: all carries resolved in O(log n) depth.
// Level 1 (stride 1) → Level 2 (stride 2). CIN absorbed into g0c upfront.
module KS4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    input  wire CIN,
    output wire S0, S1, S2, S3,
    output wire COUT
);
    wire g0=A0&B0, g1=A1&B1, g2=A2&B2, g3=A3&B3;
    wire p0=A0^B0, p1=A1^B1, p2=A2^B2, p3=A3^B3;

    // Absorb CIN into bit-0 group generate
    wire g0c = g0 | (p0 & CIN);           // group(0,-1) = c1

    // Level 1 prefix nodes (stride 1)
    wire G1_1 = g1 | (p1 & g0c);          // group(1,-1) = c2
    wire P1_1 = p1 & p0;
    wire G1_2 = g2 | (p2 & g1);           // group(2,1)
    wire P1_2 = p2 & p1;
    wire G1_3 = g3 | (p3 & g2);           // group(3,2)
    wire P1_3 = p3 & p2;

    // Level 2 prefix nodes (stride 2) — spans back to CIN
    wire c3   = G1_2 | (P1_2 & g0c);      // group(2,-1) = c3
    wire cout_s= G1_3 | (P1_3 & G1_1);    // group(3,-1) = COUT

    assign S0   = p0 ^ CIN;
    assign S1   = p1 ^ g0c;
    assign S2   = p2 ^ G1_1;
    assign S3   = p3 ^ c3;
    assign COUT = cout_s;
endmodule
