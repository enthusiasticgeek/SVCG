-- dec_2to4.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity DEC_2TO4 is
    Port ( A  : in  STD_LOGIC;
           B  : in  STD_LOGIC;
           EN : in  STD_LOGIC;
           Y0 : out STD_LOGIC;
           Y1 : out STD_LOGIC;
           Y2 : out STD_LOGIC;
           Y3 : out STD_LOGIC);
end DEC_2TO4;

architecture Behavioral of DEC_2TO4 is
begin
    Y0 <= EN and (not A) and (not B);
    Y1 <= EN and (not A) and B;
    Y2 <= EN and A       and (not B);
    Y3 <= EN and A       and B;
end Behavioral;
