module example #(
    parameter DW = 32
) (
    input  logic clk,
    input  logic rst
);

int foo_ctr = 0;
always @(posedge clk) begin
    foo_ctr <= foo_ctr + 1;
    $display("Example: %d", foo_ctr);
end

endmodule
