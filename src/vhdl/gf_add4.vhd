-- gf_add4.vhd  (4-bit GF(2^4) adder)
-- Addition in GF(2^m) is bitwise XOR; no carry exists.
-- Inputs:  A3..A0, B3..B0 — elements of GF(2^4)
-- Outputs: R3..R0 = A XOR B
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity GF_ADD4 is
    Port ( A0 : in  STD_LOGIC;
           A1 : in  STD_LOGIC;
           A2 : in  STD_LOGIC;
           A3 : in  STD_LOGIC;
           B0 : in  STD_LOGIC;
           B1 : in  STD_LOGIC;
           B2 : in  STD_LOGIC;
           B3 : in  STD_LOGIC;
           R0 : out STD_LOGIC;
           R1 : out STD_LOGIC;
           R2 : out STD_LOGIC;
           R3 : out STD_LOGIC);
end GF_ADD4;

architecture Behavioral of GF_ADD4 is
begin
    R0 <= A0 xor B0;
    R1 <= A1 xor B1;
    R2 <= A2 xor B2;
    R3 <= A3 xor B3;
end Behavioral;
