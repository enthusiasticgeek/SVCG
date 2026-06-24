-- and3.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity AND3_GATE is
    Port ( IN1  : in  STD_LOGIC;
           IN2  : in  STD_LOGIC;
           IN3  : in  STD_LOGIC;
           OUT1 : out STD_LOGIC);
end AND3_GATE;

architecture Behavioral of AND3_GATE is
begin
    OUT1 <= IN1 and IN2 and IN3;
end Behavioral;
