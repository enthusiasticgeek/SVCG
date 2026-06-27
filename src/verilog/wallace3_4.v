// wallace3_4.v  (3-operand 4-bit Wallace tree adder)
// One CSA layer reduces A+B+C to sum s[3:0] and carry co[3:0].
// Final CPA computes P = s + (co << 1).  Result is 6-bit P[5:0].
module WALLACE3_4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    input  wire C0, C1, C2, C3,
    output wire P0, P1, P2, P3, P4, P5
);
    // CSA stage
    wire s0=A0^B0^C0,  co0=(A0&B0)|(A0&C0)|(B0&C0);
    wire s1=A1^B1^C1,  co1=(A1&B1)|(A1&C1)|(B1&C1);
    wire s2=A2^B2^C2,  co2=(A2&B2)|(A2&C2)|(B2&C2);
    wire s3=A3^B3^C3,  co3=(A3&B3)|(A3&C3)|(B3&C3);

    // Final CPA: {0,s3,s2,s1,s0} + {co3,co2,co1,co0,0}
    assign P0 = s0;
    wire cc1;
    assign P1 = s1 ^ co0;    assign cc1 = s1 & co0;
    wire cc2;
    assign P2 = s2^co1^cc1;  assign cc2 = (s2&co1)|(s2&cc1)|(co1&cc1);
    wire cc3;
    assign P3 = s3^co2^cc2;  assign cc3 = (s3&co2)|(s3&cc2)|(co2&cc2);
    wire cc4;
    assign P4 = co3 ^ cc3;   assign cc4 = co3 & cc3;
    assign P5 = cc4;
endmodule
