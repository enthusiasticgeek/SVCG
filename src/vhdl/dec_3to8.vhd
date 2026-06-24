-- dec_3to8.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity DEC_3TO8 is
    Port ( A  : in  STD_LOGIC;
           B  : in  STD_LOGIC;
           C  : in  STD_LOGIC;
           EN : in  STD_LOGIC;
           Y0 : out STD_LOGIC;
           Y1 : out STD_LOGIC;
           Y2 : out STD_LOGIC;
           Y3 : out STD_LOGIC;
           Y4 : out STD_LOGIC;
           Y5 : out STD_LOGIC;
           Y6 : out STD_LOGIC;
           Y7 : out STD_LOGIC);
end DEC_3TO8;

architecture Behavioral of DEC_3TO8 is
begin
    Y0 <= EN and (not A) and (not B) and (not C);
    Y1 <= EN and (not A) and (not B) and C;
    Y2 <= EN and (not A) and B       and (not C);
    Y3 <= EN and (not A) and B       and C;
    Y4 <= EN and A       and (not B) and (not C);
    Y5 <= EN and A       and (not B) and C;
    Y6 <= EN and A       and B       and (not C);
    Y7 <= EN and A       and B       and C;
end Behavioral;
