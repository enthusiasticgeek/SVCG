// array_mult4.v  (4x4 unsigned array multiplier)
// Gate-level structure: AND partial-product array + HA/FA reduction rows.
module ARRAY_MULT4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    output wire P0, P1, P2, P3, P4, P5, P6, P7
);
    // Partial products
    wire pp00=A0&B0, pp10=A1&B0, pp20=A2&B0, pp30=A3&B0;
    wire pp01=A0&B1, pp11=A1&B1, pp21=A2&B1, pp31=A3&B1;
    wire pp02=A0&B2, pp12=A1&B2, pp22=A2&B2, pp32=A3&B2;
    wire pp03=A0&B3, pp13=A1&B3, pp23=A2&B3, pp33=A3&B3;

    // Row 1: add B0 and B1 rows
    wire r1s1 = pp10^pp01,          r1c1 = pp10&pp01;
    wire r1s2 = pp20^pp11^r1c1,     r1c2 = (pp20&pp11)|(pp20&r1c1)|(pp11&r1c1);
    wire r1s3 = pp30^pp21^r1c2,     r1c3 = (pp30&pp21)|(pp30&r1c2)|(pp21&r1c2);
    wire r1s4 = pp31^r1c3,          r1c4 = pp31&r1c3;

    // Row 2: add B2 row
    wire r2s2 = r1s2^pp02,          r2c2 = r1s2&pp02;
    wire r2s3 = r1s3^pp12^r2c2,     r2c3 = (r1s3&pp12)|(r1s3&r2c2)|(pp12&r2c2);
    wire r2s4 = r1s4^pp22^r2c3,     r2c4 = (r1s4&pp22)|(r1s4&r2c3)|(pp22&r2c3);
    wire r2s5 = r1c4^pp32^r2c4,     r2c5 = (r1c4&pp32)|(r1c4&r2c4)|(pp32&r2c4);

    // Row 3: add B3 row
    wire r3s3 = r2s3^pp03,          r3c3 = r2s3&pp03;
    wire r3s4 = r2s4^pp13^r3c3,     r3c4 = (r2s4&pp13)|(r2s4&r3c3)|(pp13&r3c3);
    wire r3s5 = r2s5^pp23^r3c4,     r3c5 = (r2s5&pp23)|(r2s5&r3c4)|(pp23&r3c4);
    wire r3s6 = r2c5^pp33^r3c5,     r3c6 = (r2c5&pp33)|(r2c5&r3c5)|(pp33&r3c5);

    assign P0=pp00, P1=r1s1, P2=r2s2, P3=r3s3;
    assign P4=r3s4, P5=r3s5, P6=r3s6, P7=r3c6;
endmodule
