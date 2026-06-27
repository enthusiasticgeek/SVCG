-- csa.vhd  (1-bit carry save adder / 3:2 compressor)
-- Takes three inputs A, B, C and produces a partial sum SO and carry CO
-- without propagating the carry — the CO is left to be summed at the
-- next tree level.  Used as the building block in Wallace-tree multipliers.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity CSA is
    Port ( A  : in  STD_LOGIC;
           B  : in  STD_LOGIC;
           C  : in  STD_LOGIC;
           SO : out STD_LOGIC;
           CO : out STD_LOGIC);
end CSA;

architecture Behavioral of CSA is
begin
    SO <= A xor B xor C;
    CO <= (A and B) or (A and C) or (B and C);
end Behavioral;
