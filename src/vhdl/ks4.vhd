-- ks4.vhd  (4-bit Kogge-Stone parallel prefix adder)
-- All carries are computed in two parallel prefix levels (O(log n) depth).
-- Level 1 (stride 1): 3 prefix nodes covering adjacent pairs.
-- Level 2 (stride 2): 2 prefix nodes covering spans back to CIN.
-- CIN is absorbed into the bit-0 group generate before level 1.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity KS4 is
    Port ( A0   : in  STD_LOGIC;
           A1   : in  STD_LOGIC;
           A2   : in  STD_LOGIC;
           A3   : in  STD_LOGIC;
           B0   : in  STD_LOGIC;
           B1   : in  STD_LOGIC;
           B2   : in  STD_LOGIC;
           B3   : in  STD_LOGIC;
           CIN  : in  STD_LOGIC;
           S0   : out STD_LOGIC;
           S1   : out STD_LOGIC;
           S2   : out STD_LOGIC;
           S3   : out STD_LOGIC;
           COUT : out STD_LOGIC);
end KS4;

architecture Behavioral of KS4 is
    signal g0, g1, g2, g3 : STD_LOGIC;  -- bit-level generate: gi = Ai AND Bi
    signal p0, p1, p2, p3 : STD_LOGIC;  -- bit-level propagate: pi = Ai XOR Bi
    signal g0c             : STD_LOGIC;  -- g0 with CIN absorbed: group(0,-1)
    -- Level-1 prefix nodes (stride 1)
    signal G1_1, P1_1     : STD_LOGIC;  -- group(1,-1) = carry into bit 2
    signal G1_2, P1_2     : STD_LOGIC;  -- group(2, 1) — partial span
    signal G1_3, P1_3     : STD_LOGIC;  -- group(3, 2) — partial span
    -- Level-2 prefix nodes (stride 2) — complete spans to CIN
    signal c3, cout_s      : STD_LOGIC;
begin
    g0 <= A0 and B0;  g1 <= A1 and B1;
    g2 <= A2 and B2;  g3 <= A3 and B3;
    p0 <= A0 xor B0;  p1 <= A1 xor B1;
    p2 <= A2 xor B2;  p3 <= A3 xor B3;

    -- Absorb CIN: group(0,-1) = c1 (carry into bit 1)
    g0c <= g0 or (p0 and CIN);

    -- Level 1
    G1_1 <= g1 or (p1 and g0c);  P1_1 <= p1 and p0;  -- group(1,-1) = c2
    G1_2 <= g2 or (p2 and g1);   P1_2 <= p2 and p1;  -- group(2,1)
    G1_3 <= g3 or (p3 and g2);   P1_3 <= p3 and p2;  -- group(3,2)

    -- Level 2
    c3    <= G1_2 or (P1_2 and g0c);   -- group(2,-1) = c3
    cout_s <= G1_3 or (P1_3 and G1_1); -- group(3,-1) = COUT

    S0   <= p0 xor CIN;
    S1   <= p1 xor g0c;
    S2   <= p2 xor G1_1;
    S3   <= p3 xor c3;
    COUT <= cout_s;
end Behavioral;
