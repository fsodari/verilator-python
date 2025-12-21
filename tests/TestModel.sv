module TestModel #(
    parameter DW = 24
) (
    input  logic clk,
    input  logic [DW-1:0] d,
    output logic signed [DW-1:0] q
);

always @(posedge clk) begin
    q <= d;
end

endmodule