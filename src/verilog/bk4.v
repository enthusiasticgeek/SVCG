// bk4.v  (4-bit Brent-Kung parallel prefix adder)
// Up-sweep: 2 levels build COUT with half the nodes of Kogge-Stone.
// Down-sweep: 1 level distributes intermediate carry c3.
module BK4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    input  wire CIN,
    output wire S0, S1, S2, S3,
    output wire COUT
);
    wire g0=A0&B0, g1=A1&B1, g2=A2&B2, g3=A3&B3;
    wire p0=A0^B0, p1=A1^B1, p2=A2^B2, p3=A3^B3;

    wire g0c = g0 | (p0 & CIN);           // group(0,-1) = c1

    // Up-sweep level 1 (stride 1, odd positions)
    wire G1_1 = g1 | (p1 & g0c);          // group(1,-1) = c2
    wire P1_1 = p1 & p0;
    wire G1_3 = g3 | (p3 & g2);           // group(3,2)
    wire P1_3 = p3 & p2;

    // Up-sweep level 2 (stride 2) → COUT
    wire G2_3 = G1_3 | (P1_3 & G1_1);    // group(3,-1)

    // Down-sweep: fill in c3
    wire c3   = g2 | (p2 & G1_1);         // group(2,-1)

    assign S0   = p0 ^ CIN;
    assign S1   = p1 ^ g0c;
    assign S2   = p2 ^ G1_1;
    assign S3   = p3 ^ c3;
    assign COUT = G2_3;
endmodule
