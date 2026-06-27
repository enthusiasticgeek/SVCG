// booth4_mult4.v  (4-bit signed radix-4 Modified Booth multiplier)
// Two partial products (vs four for radix-2); each is 0/±A/±2A.
module BOOTH4_MULT4 (
    input  wire A0, A1, A2, A3,
    input  wire B0, B1, B2, B3,
    output wire P0, P1, P2, P3, P4, P5, P6, P7
);
    reg signed [8:0] acc;
    reg signed [5:0] A_v, pp;   // 6-bit to avoid ±2A overflow when A=-8
    reg signed [3:0] B_v;
    reg [2:0] grp;

    always @(*) begin
        A_v = {A3, A3, A3, A2, A1, A0};   // sign-extend to 6-bit
        B_v = {B3, B2, B1, B0};
        acc = 9'sd0;

        // Group 0: (B1, B0, 0)
        grp = {B_v[1], B_v[0], 1'b0};
        case (grp)
            3'b001, 3'b010:  pp =  A_v;
            3'b011:          pp =  A_v << 1;
            3'b100:          pp = -(A_v << 1);
            3'b101, 3'b110:  pp = -A_v;
            default:         pp = 6'sd0;
        endcase
        acc = acc + {{3{pp[5]}}, pp};

        // Group 1: (B3, B2, B1) at weight 4
        grp = {B_v[3], B_v[2], B_v[1]};
        case (grp)
            3'b001, 3'b010:  pp =  A_v;
            3'b011:          pp =  A_v << 1;
            3'b100:          pp = -(A_v << 1);
            3'b101, 3'b110:  pp = -A_v;
            default:         pp = 6'sd0;
        endcase
        acc = acc + ({{3{pp[5]}}, pp} << 2);
    end

    assign {P7,P6,P5,P4,P3,P2,P1,P0} = acc[7:0];
endmodule
