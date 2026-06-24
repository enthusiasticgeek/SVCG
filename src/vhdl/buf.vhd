-- buf.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity BUF_GATE is
    Port ( IN1  : in  STD_LOGIC;
           OUT1 : out STD_LOGIC);
end BUF_GATE;

architecture Behavioral of BUF_GATE is
begin
    OUT1 <= IN1;
end Behavioral;
