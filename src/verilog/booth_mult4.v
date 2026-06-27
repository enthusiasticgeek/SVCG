// booth_mult4.v  (4-bit signed Booth multiplier, radix-2)
// Radix-2 Booth recoding: examine (Q[i], Q[i-1]) pairs with Q[-1]=0.
//   00 or 11 -> add 0
//   01       -> add multiplicand A
//   10       -> subtract multiplicand A
module BOOTH_MULT4 (
    input  wire A0, A1, A2, A3,  // multiplicand (signed, LSB first)
    input  wire B0, B1, B2, B3,  // multiplier   (signed, LSB first)
    output wire P0, P1, P2, P3, P4, P5, P6, P7
);
    wire signed [3:0] A_s = {A3, A2, A1, A0};
    wire signed [4:0] B_s = {B3, B2, B1, B0, 1'b0};  // append Q[-1]=0

    // Four partial products via Booth recoding
    // pp[i] = A * 2^i  if (B[i], B[i-1]) == 01
    //       = -A * 2^i if (B[i], B[i-1]) == 10
    //       = 0        otherwise

    function [8:0] booth_pp;
        input signed [3:0] A_in;
        input qi, qi1;
        input integer sh;
        reg signed [8:0] tmp;
        begin
            if (qi == 1'b0 && qi1 == 1'b1)
                tmp = ($signed({{5{A_in[3]}}, A_in}) <<< sh);
            else if (qi == 1'b1 && qi1 == 1'b0)
                tmp = ($signed(-{{5{A_in[3]}}, A_in}) <<< sh);
            else
                tmp = 9'sd0;
            booth_pp = tmp;
        end
    endfunction

    wire signed [8:0] pp0 = booth_pp(A_s, B_s[1], B_s[0], 0);
    wire signed [8:0] pp1 = booth_pp(A_s, B_s[2], B_s[1], 1);
    wire signed [8:0] pp2 = booth_pp(A_s, B_s[3], B_s[2], 2);
    wire signed [8:0] pp3 = booth_pp(A_s, B_s[4], B_s[3], 3);

    wire signed [8:0] prod = pp0 + pp1 + pp2 + pp3;

    assign {P7,P6,P5,P4,P3,P2,P1,P0} = prod[7:0];
endmodule
