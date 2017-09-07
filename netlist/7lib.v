module FA1D1 ( A, B, CI, S, CO) 
input A, B, CI
output S, CO

timing A CO, 1.1
timing B CO, 1.2
timing CI CO, 1.3
timing A S, 1.4
timing B S, 1.5
timing CI S, 1.6

module DFQD1 (D, CP, Q)
input D, CP
output Q

timing D Q, 1.0
timing CP Q, 2.0
