-- and.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity AND_GATE is
    Port ( IN1 : in  STD_LOGIC;
           IN2 : in  STD_LOGIC;
           OUT1 : out  STD_LOGIC);
end AND_GATE;

architecture Behavioral of AND_GATE is
begin
    OUT1 <= IN1 and IN2;
end Behavioral;
