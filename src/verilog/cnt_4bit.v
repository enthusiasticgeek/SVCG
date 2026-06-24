// cnt_4bit.v  4-bit synchronous up counter
module CNT_4BIT (
    input  wire CLK,
    input  wire RST,
    input  wire EN,
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
        else if (EN)
            count <= count + 1;
    end
    assign Q0 = count[0];
    assign Q1 = count[1];
    assign Q2 = count[2];
    assign Q3 = count[3];
    assign TC = (count == 4'b1111) && EN;
endmodule
