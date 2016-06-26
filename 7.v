
module rca_8bit ( A, B, CI, clk, CO, S );
  input [7:0] A;
  input [7:0] B;
  output [7:0] S;
  input CI, clk;
  output CO;
  wire   B0, B7, B6, B5, B3, B2, B1, B4, A4, A7, A6, A5, A3, A2, A1, A0,
         net127, net125, net122, net124, net128, net126, net123, CI0;

  DFQD1 I237 ( .D(B[0]), .CP(clk), .Q(B0) );
  DFQD1 I236 ( .D(B[7]), .CP(clk), .Q(B7) );
  DFQD1 I235 ( .D(B[6]), .CP(clk), .Q(B6) );
  DFQD1 I234 ( .D(B[5]), .CP(clk), .Q(B5) );
  DFQD1 I233 ( .D(B[3]), .CP(clk), .Q(B3) );
  DFQD1 I232 ( .D(B[2]), .CP(clk), .Q(B2) );
  DFQD1 I231 ( .D(B[1]), .CP(clk), .Q(B1) );
  DFQD1 I230 ( .D(B[4]), .CP(clk), .Q(B4) );
  DFQD1 I221 ( .D(A[4]), .CP(clk), .Q(A4) );
  DFQD1 I220 ( .D(A[7]), .CP(clk), .Q(A7) );
  DFQD1 I219 ( .D(A[6]), .CP(clk), .Q(A6) );
  DFQD1 I218 ( .D(A[5]), .CP(clk), .Q(A5) );
  DFQD1 I217 ( .D(A[3]), .CP(clk), .Q(A3) );
  DFQD1 I216 ( .D(A[2]), .CP(clk), .Q(A2) );
  DFQD1 I215 ( .D(A[1]), .CP(clk), .Q(A1) );
  DFQD1 I214 ( .D(A[0]), .CP(clk), .Q(A0) );
  DFQD1 ICI  ( .D(CI), .CP(clk), .Q(CI0) );
  FA1D1 I7 ( .A(A7), .B(B7), .CI(net127), .S(S[7]), .CO(CO) );
  FA1D1 I6 ( .A(A6), .B(B6), .CI(net125), .S(S[6]), .CO(net127) );
  FA1D1 I5 ( .A(A5), .B(B5), .CI(net122), .S(S[5]), .CO(net125) );
  FA1D1 I4 ( .A(A4), .B(B4), .CI(net124), .S(S[4]), .CO(net122) );
  FA1D1 I3 ( .A(A3), .B(B3), .CI(net128), .S(S[3]), .CO(net124) );
  FA1D1 I2 ( .A(A2), .B(B2), .CI(net126), .S(S[2]), .CO(net128) );
  FA1D1 I1 ( .A(A1), .B(B1), .CI(net123), .S(S[1]), .CO(net126) );
  FA1D1 I0 ( .A(A0), .B(B0), .CI(CI0), .S(S[0]), .CO(net123) );
endmodule

