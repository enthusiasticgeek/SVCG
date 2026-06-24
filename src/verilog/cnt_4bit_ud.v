// cnt_4bit_ud.v  4-bit synchronous up/down counter
module CNT_4BIT_UD (
    input  wire CLK,
    input  wire RST,
    input  wire EN,
    input  wire DIR,
    output wire Q0,
    output wire Q1,
    output wire Q2,
    output wire Q3,
    output wire TC
);
    reg [3:0] count;
    always @(posedge CLK or posedge RST) begin
        if (RST)
            count <= 4'b0000;
        else if (EN) begin
            if (DIR)
                count <= count + 1;
            else
                count <= count - 1;
        end
    end
    assign Q0 = count[0];
    assign Q1 = count[1];
    assign Q2 = count[2];
    assign Q3 = count[3];
    assign TC = ((DIR && count == 4'b1111) || (!DIR && count == 4'b0000)) && EN;
endmodule
