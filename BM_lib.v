module OAOAI2111HSV0 ( ZN, A1, A2, B, C, D)
input A1, A2, B, C, D
output ZN

timing A1 ZN, 0.06069
timing A2 ZN, 0.06255
timing B ZN, 0.04426
timing C ZN, 0.02683
timing D ZN, 0.01763

module CLKNHSV0 (ZN, I)
input I
output ZN

timing I ZN, 0.011565

module AOI21HSV0 ( ZN, A1, A2, B)
input A1, A2, B
output ZN

timing A1 ZN, 0.06069
timing A2 ZN, 0.06255
timing B ZN, 0.04426

module OAI211HSV0 ( ZN, A1, A2, B, C)
input A1, A2, B, C
output ZN

timing A1 ZN, 0.06069
timing A2 ZN, 0.06255
timing B ZN, 0.04426
timing C ZN, 0.02683

module CLKNAND2HSV0 ( ZN, A1, A2)
input A1, A2
output ZN

timing A1 ZN, 0.01502
timing A2 ZN, 0.01676

module NOR2HSV0 ( ZN, A1, A2)
input A1, A2
output ZN

timing A1 ZN, 0.01808
timing A2 ZN, 0.02020

module AOI211HSV0 ( ZN, A1, A2, B, C) 
input A1, A2, B, C
output ZN

timing A1 ZN, 0.03868
timing A2 ZN, 0.04225
timing B ZN, 0.02554
timing C ZN, 0.02399

module OAI21HSV0 ( ZN, A1, A2, B) 
input A1, A2, B
output ZN

timing A1 ZN, 0.02779
timing A2 ZN, 0.03027
timing B ZN, 0.01836

module NOR4HSV0 ( ZN, A1, A2, A3, A4)
input A1, A2, A3, A4
output ZN

timing A1 ZN, 0.03448
timing A2 ZN, 0.03973
timing A3 ZN, 0.02946
timing A4 ZN, 0.04461

module AO21HSV0 ( Z, A1, A2, B)
input A1, A2, B
output Z

timing A1 Z, 0.04796
timing A2 Z, 0.05049
timing B Z, 0.03231

module NAND4HSV0 ( ZN, A1, A2, A3, A4)
input A1, A2, A3, A4
output ZN

timing A1 ZN, 0.02864
timing A2 ZN, 0.03355
timing A3 ZN, 0.03651
timing A4 ZN, 0.03829

module AOI222HSV0 ( ZN, A1, A2, B1, B2, C1, C2)
input A1, A2, B1, B2, C1, C2
output ZN

timing A1 ZN, 0.03362
timing A2 ZN, 0.03360
timing B1 ZN, 0.04398
timing B2 ZN, 0.04208
timing C1 ZN, 0.04656
timing C2 ZN, 0.04884

module OA211HSV0 ( Z, A1, A2, B, C)
input A1, A2, B, C
output Z

timing A1 Z, 0.05551
timing A2 Z, 0.05904
timing B Z, 0.05504
timing C Z, 0.05723

module OAI222HSV0 ( ZN, A1, A2, B1, B2, C1, C2) 
input A1, A2, B1, B2, C1, C2
output ZN

timing A1 ZN, 0.04558
timing A2 ZN, 0.04876
timing B1 ZN, 0.05195
timing B2 ZN, 0.05769
timing C1 ZN, 0.03787
timing C2 ZN, 0.04114

module AND4HSV0 ( Z, A1, A2, A3, A4)
input A1, A2, A3, A4
output Z

timing A1 Z, 0.05432
timing A2 Z, 0.05897
timing A3 Z, 0.06192
timing A4 Z, 0.06547

module OAI221HSV0 ( ZN, A1, A2, B1, B2, C)
input A1, A2, B1, B2, C
output ZN

timing A1 ZN, 0.03834
timing A2 ZN, 0.04093
timing B1 ZN, 0.04470
timing B2 ZN, 0.04764
timing C ZN, 0.02415

module AOI32HSV0 ( ZN, A1, A2, A3, B1, B2) 
input A1, A2, A3, B1, B2
output ZN

timing A1 ZN, 0.03720
timing A2 ZN, 0.04068
timing A3 ZN, 0.04578
timing B1 ZN, 0.01916
timing B2 ZN, 0.02159

module OAI33HSV1 ( ZN, A1, A2, A3, B1, B2, B3)
input A1, A2, A3, B1, B2, B3
output ZN

timing A1 ZN, 0.04469
timing A2 ZN, 0.05146
timing A3 ZN, 0.05414
timing B1 ZN, 0.03136
timing B2 ZN, 0.03843
timing B3 ZN, 0.04249

module NOR3HSV0 ( ZN, A1, A2, A3)
input A1, A2, A3
output ZN

timing A1 ZN, 0.02595
timing A2 ZN, 0.02945
timing A3 ZN, 0.03105

module AOI31HSV0 ( ZN, A1, A2, A3, B)
input A1, A2, A3, B
output ZN

timing A1 ZN, 0.03265
timing A2 ZN, 0.03635
timing A3 ZN, 0.03846
timing B ZN, 0.01477

module OAI31HSV0 ( ZN, A1, A2, A3, B)
input A1, A2, A3, B
output ZN

timing A1 ZN, 0.03505
timing A2 ZN, 0.04026
timing A3 ZN, 0.04293
timing B ZN, 0.01942

module NAND3HSV0 ( ZN, A1, A2, A3)
input A1, A2, A3
output ZN

timing A1 ZN, 0.02263
timing A2 ZN, 0.02474
timing A3 ZN, 0.02625

module INOR2HSV0 ( ZN, A1, B1)
input A1, B1
output ZN

timing A1 ZN, 0.03383
timing B1 ZN, 0.01961

module OA33HSV0 ( Z, A1, A2, A3, B1, B2, B3) 
input A1, A2, A3, B1, B2, B3
output Z

timing A1 Z, 0.06489
timing A2 Z, 0.07183
timing A3 Z, 0.07346
timing B1 Z, 0.07890
timing B2 Z, 0.08357
timing B3 Z, 0.08970

module AND2HSV0 ( Z, A1, A2)
input A1, A2
output Z

timing A1 Z, 0.03439
timing A2 Z, 0.03692

module AOI33HSV0 ( ZN, A1, A2, A3, B1, B2, B3)
input A1, A2, A3, B1, B2, B3
output ZN

timing A1 ZN, 0.04113
timing A2 ZN, 0.04383
timing A3 ZN, 0.04556
timing B1 ZN, 0.02581
timing B2 ZN, 0.02961
timing B3 ZN, 0.03097

module AOI221HSV0 ( ZN, A1, A2, B1, B2, C)
input A1, A2, B1, B2, C
output ZN

timing A1 ZN, 0.04160
timing A2 ZN, 0.04461
timing B1 ZN, 0.03418
timing B2 ZN, 0.03789
timing C ZN, 0.02038

module OAI22HSV0 ( ZN, A1, A2, B1, B2)
input A1, A2, B1, B2
output ZN

timing A1 ZN, 0.04935
timing A2 ZN, 0.02888
timing B1 ZN, 0.03316
timing B2 ZN, 0.03657

module IAO22HSV0 ( ZN, A1, A2, B1, B2)
input A1, A2, B1, B2
output ZN

timing A1 ZN, 0.04384
timing A2 ZN, 0.04344
timing B1 ZN, 0.02782
timing B2 ZN, 0.02974
