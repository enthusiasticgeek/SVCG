-- bk4.vhd  (4-bit Brent-Kung parallel prefix adder)
-- Up-sweep builds COUT in ceil(log2 n) levels using fewer nodes than KS.
-- Down-sweep fills intermediate carries in one additional level.
-- Total 3 levels vs KS 2 levels, but half the nodes at each level.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity BK4 is
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
end BK4;

architecture Behavioral of BK4 is
    signal g0, g1, g2, g3 : STD_LOGIC;
    signal p0, p1, p2, p3 : STD_LOGIC;
    signal g0c             : STD_LOGIC;  -- group(0,-1): CIN absorbed
    -- Up-sweep level 1 (stride 1, odd positions only)
    signal G1_1, P1_1     : STD_LOGIC;  -- group(1,-1) = c2
    signal G1_3, P1_3     : STD_LOGIC;  -- group(3,2)
    -- Up-sweep level 2 (stride 2)
    signal G2_3            : STD_LOGIC;  -- group(3,-1) = COUT
    -- Down-sweep level 1
    signal c3              : STD_LOGIC;  -- group(2,-1) = c3
begin
    g0 <= A0 and B0;  g1 <= A1 and B1;
    g2 <= A2 and B2;  g3 <= A3 and B3;
    p0 <= A0 xor B0;  p1 <= A1 xor B1;
    p2 <= A2 xor B2;  p3 <= A3 xor B3;

    -- Absorb CIN
    g0c <= g0 or (p0 and CIN);

    -- Up-sweep level 1: merge adjacent pairs at odd positions
    G1_1 <= g1 or (p1 and g0c);  P1_1 <= p1 and p0;  -- group(1,-1) = c2
    G1_3 <= g3 or (p3 and g2);   P1_3 <= p3 and p2;  -- group(3,2)

    -- Up-sweep level 2: merge stride-2 pair → COUT
    G2_3 <= G1_3 or (P1_3 and G1_1);  -- group(3,-1)

    -- Down-sweep level 1: fill in c3 using up-sweep results
    c3 <= g2 or (p2 and G1_1);    -- group(2,-1)

    S0   <= p0 xor CIN;
    S1   <= p1 xor g0c;
    S2   <= p2 xor G1_1;
    S3   <= p3 xor c3;
    COUT <= G2_3;
end Behavioral;
