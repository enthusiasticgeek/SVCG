-- dadda4.vhd  (3-operand 4-bit Dadda tree adder)
-- Dadda reduction: use the minimum number of HA/FA to reduce column heights
-- to the Dadda target sequence (2,2,2,...) before the final CPA.
-- For 3 operands the CSA stage reduces height 3->2 exactly as Wallace,
-- so the result is identical but the derivation follows Dadda's method.
-- Inputs:  A3..A0, B3..B0, C3..C0 — 4-bit unsigned
-- Outputs: P5..P0 = A + B + C  (6-bit sum, max = 45)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity DADDA4 is
    Port ( A0 : in  STD_LOGIC;
           A1 : in  STD_LOGIC;
           A2 : in  STD_LOGIC;
           A3 : in  STD_LOGIC;
           B0 : in  STD_LOGIC;
           B1 : in  STD_LOGIC;
           B2 : in  STD_LOGIC;
           B3 : in  STD_LOGIC;
           C0 : in  STD_LOGIC;
           C1 : in  STD_LOGIC;
           C2 : in  STD_LOGIC;
           C3 : in  STD_LOGIC;
           P0 : out STD_LOGIC;
           P1 : out STD_LOGIC;
           P2 : out STD_LOGIC;
           P3 : out STD_LOGIC;
           P4 : out STD_LOGIC;
           P5 : out STD_LOGIC);
end DADDA4;

architecture Behavioral of DADDA4 is
    -- Dadda stage 1: reduce each column from height 3 to height 2 using FA/HA.
    -- Column 0 (weight 1):  A0, B0, C0  -> FA -> s0, co0
    -- Column 1 (weight 2):  A1, B1, C1  -> FA -> s1, co1
    -- Column 2 (weight 4):  A2, B2, C2  -> FA -> s2, co2
    -- Column 3 (weight 8):  A3, B3, C3  -> FA -> s3, co3
    signal s0,s1,s2,s3     : STD_LOGIC;
    signal co0,co1,co2,co3 : STD_LOGIC;
    -- Final CPA carry chain
    signal cc1,cc2,cc3,cc4 : STD_LOGIC;
begin
    -- Dadda stage 1: 4 full adders (one per column, height 3->2)
    s0  <= A0 xor B0 xor C0;
    co0 <= (A0 and B0) or (A0 and C0) or (B0 and C0);

    s1  <= A1 xor B1 xor C1;
    co1 <= (A1 and B1) or (A1 and C1) or (B1 and C1);

    s2  <= A2 xor B2 xor C2;
    co2 <= (A2 and B2) or (A2 and C2) or (B2 and C2);

    s3  <= A3 xor B3 xor C3;
    co3 <= (A3 and B3) or (A3 and C3) or (B3 and C3);

    -- Final CPA: add (s3 s2 s1 s0) + (co3 co2 co1 co0) with ripple carry
    P0  <= s0;
    P1  <= s1 xor co0;               cc1 <= s1 and co0;
    P2  <= s2 xor co1 xor cc1;       cc2 <= (s2 and co1) or (s2 and cc1) or (co1 and cc1);
    P3  <= s3 xor co2 xor cc2;       cc3 <= (s3 and co2) or (s3 and cc2) or (co2 and cc2);
    P4  <= co3 xor cc3;              cc4 <= co3 and cc3;
    P5  <= cc4;
end Behavioral;
