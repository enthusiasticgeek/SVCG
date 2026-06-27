-- cla4.vhd  (4-bit carry lookahead adder)
-- Computes carry signals in parallel using generate/propagate logic,
-- eliminating the ripple delay of a simple RCA.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity CLA4 is
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
end CLA4;

architecture Behavioral of CLA4 is
    signal g0, g1, g2, g3 : STD_LOGIC;  -- generate: gi = Ai AND Bi
    signal p0, p1, p2, p3 : STD_LOGIC;  -- propagate: pi = Ai XOR Bi
    signal c1, c2, c3, c4 : STD_LOGIC;  -- lookahead carries
begin
    g0 <= A0 and B0;
    g1 <= A1 and B1;
    g2 <= A2 and B2;
    g3 <= A3 and B3;
    p0 <= A0 xor B0;
    p1 <= A1 xor B1;
    p2 <= A2 xor B2;
    p3 <= A3 xor B3;

    -- Carry lookahead equations
    c1 <= g0 or (p0 and CIN);
    c2 <= g1 or (p1 and g0) or (p1 and p0 and CIN);
    c3 <= g2 or (p2 and g1) or (p2 and p1 and g0) or (p2 and p1 and p0 and CIN);
    c4 <= g3 or (p3 and g2) or (p3 and p2 and g1) or (p3 and p2 and p1 and g0)
              or (p3 and p2 and p1 and p0 and CIN);

    S0   <= p0 xor CIN;
    S1   <= p1 xor c1;
    S2   <= p2 xor c2;
    S3   <= p3 xor c3;
    COUT <= c4;
end Behavioral;
