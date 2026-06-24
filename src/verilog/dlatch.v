// dlatch.v  D latch (transparent when EN=1)
module DLATCH (
    input  wire D,
    input  wire EN,
    output reg  Q,
    output wire Q_bar
);
    always @(*) begin
        if (EN)
            Q = D;
    end
    assign Q_bar = ~Q;
endmodule
