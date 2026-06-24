// srlatch.v  NOR-based SR latch
module SRLATCH (
    input  wire S,
    input  wire R,
    output wire Q,
    output wire Q_bar
);
    assign Q     = ~(R | Q_bar);
    assign Q_bar = ~(S | Q);
endmodule
