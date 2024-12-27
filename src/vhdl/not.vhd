-- not.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity NOT_GATE is
    Port ( IN1 : in  STD_LOGIC;
           OUT1 : out  STD_LOGIC);
end NOT_GATE;

architecture Behavioral of NOT_GATE is
begin
    OUT1 <= not IN1;
end Behavioral;
