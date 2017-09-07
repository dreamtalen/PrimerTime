# Short Path Padding

> Short Path Padding with Multiple-Vt cells for Wide-Pulsed-Latch Based Circuits at Ultra-Low Voltage

### Publication

**Yongming Ding**, Wei Jin, Guanghui He, Weifeng He. “Short Path Padding with Multiple-Vt cells for Wide-Pulsed-Latch Based Circuits at Ultra-Low Voltage.” *IEEE International Conference on ASIC* (2017). Accepted.

### Abstract

> This paper presents a short path padding technique for wide-pulsed-latch based circuit design in near/sub-threshold (Vt) regime. To reduce the additional hardware cost, multiple-Vt buffer cells are used to pad the short paths to avoid hold time violations. To reduce the runtime of the padding algorithm further, step-by-step based and path group based short path padding schemes are proposed. Employing the integer linear programming (ILP) solver, an automatic short path padding software is developed. Experimental results show that our proposed short path padding technique can reduce 52.3% hardware padding cost on verage. Furthermore, the runtime of padding software is reduced 79.6%, 74.95% and 80.88%, by using the step-by-step based, path group based and the hybrid scheme, respectively. In consequence, this technique supports up to a wide pulse of 1/3 cycle time in the pulsed-latch pipelines to enable a large time-borrowing capability and tolerance of variations. 

### Usage

- Short_path_padding_with_multiple-Vt_cells.py: Baseline algorithm
- Step_by_step_based_scheme.py: Step-by-step based short path padding scheme
- Path_group_based_scheme.py: Path group based short path padding scheme
- Hybrid_scheme.py: The hybrid scheme based on step-by-step and path group
- Dynamic_programming_scheme.py: Dynamic programming implemented method without Integer Linear Programming

​		
​	