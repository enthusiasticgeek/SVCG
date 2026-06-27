-- gf_mul4.vhd  (4-bit GF(2^4) multiplier)
-- Field: GF(2^4) with primitive polynomial p(x) = x^4 + x + 1 (0x13).
-- Multiplication is polynomial multiply mod p(x), all arithmetic in GF(2) (XOR/AND).
-- Inputs:  A3..A0, B3..B0 — 4-bit field elements (A3=MSB)
-- Outputs: R3..R0 = A * B in GF(2^4)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity GF_MUL4 is
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
end GF_MUL4;

architecture Behavioral of GF_MUL4 is
    -- Partial products: p[i][j] = A_i AND B_j
    signal p00,p01,p02,p03 : STD_LOGIC;
    signal p10,p11,p12,p13 : STD_LOGIC;
    signal p20,p21,p22,p23 : STD_LOGIC;
    signal p30,p31,p32,p33 : STD_LOGIC;
    -- Intermediate unreduced 7-bit polynomial coefficients c[0..6]
    signal c0,c1,c2,c3,c4,c5,c6 : STD_LOGIC;
begin
    -- Partial products
    p00 <= A0 and B0;  p01 <= A0 and B1;  p02 <= A0 and B2;  p03 <= A0 and B3;
    p10 <= A1 and B0;  p11 <= A1 and B1;  p12 <= A1 and B2;  p13 <= A1 and B3;
    p20 <= A2 and B0;  p21 <= A2 and B1;  p22 <= A2 and B2;  p23 <= A2 and B3;
    p30 <= A3 and B0;  p31 <= A3 and B1;  p32 <= A3 and B2;  p33 <= A3 and B3;

    -- Unreduced product coefficients (degree 0..6)
    c0 <= p00;
    c1 <= p01 xor p10;
    c2 <= p02 xor p11 xor p20;
    c3 <= p03 xor p12 xor p21 xor p30;
    c4 <= p13 xor p22 xor p31;
    c5 <= p23 xor p32;
    c6 <= p33;

    -- Reduce mod x^4 + x + 1:
    --   x^4 = x + 1  =>  c4*x^4 = c4*(x+1) = c4*x + c4
    --   x^5 = x^2+x  =>  c5*x^5 = c5*x^2 + c5*x
    --   x^6 = x^3+x^2 => c6*x^6 = c6*x^3 + c6*x^2
    R0 <= c0 xor c4;
    R1 <= c1 xor c4 xor c5;
    R2 <= c2 xor c5 xor c6;
    R3 <= c3 xor c6;
end Behavioral;
