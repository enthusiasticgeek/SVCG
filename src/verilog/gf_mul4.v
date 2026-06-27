// gf_mul4.v  (4-bit GF(2^4) multiplier)
// Field: GF(2^4) with primitive polynomial p(x) = x^4 + x + 1 (0x13).
// Multiply two 4-bit field elements; reduce mod p(x) using XOR.
module GF_MUL4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    output wire R0, R1, R2, R3
);
    // Partial products
    wire p00=A0&B0, p01=A0&B1, p02=A0&B2, p03=A0&B3;
    wire p10=A1&B0, p11=A1&B1, p12=A1&B2, p13=A1&B3;
    wire p20=A2&B0, p21=A2&B1, p22=A2&B2, p23=A2&B3;
    wire p30=A3&B0, p31=A3&B1, p32=A3&B2, p33=A3&B3;

    // Unreduced 7-bit product
    wire c0 = p00;
    wire c1 = p01 ^ p10;
    wire c2 = p02 ^ p11 ^ p20;
    wire c3 = p03 ^ p12 ^ p21 ^ p30;
    wire c4 = p13 ^ p22 ^ p31;
    wire c5 = p23 ^ p32;
    wire c6 = p33;

    // Reduce mod x^4+x+1: x^4=x+1, x^5=x^2+x, x^6=x^3+x^2
    assign R0 = c0 ^ c4;
    assign R1 = c1 ^ c4 ^ c5;
    assign R2 = c2 ^ c5 ^ c6;
    assign R3 = c3 ^ c6;
endmodule
