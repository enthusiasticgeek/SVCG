-- and4.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity AND4_GATE is
    Port ( IN1  : in  STD_LOGIC;
           IN2  : in  STD_LOGIC;
           IN3  : in  STD_LOGIC;
           IN4  : in  STD_LOGIC;
           OUT1 : out STD_LOGIC);
end AND4_GATE;

architecture Behavioral of AND4_GATE is
begin
    OUT1 <= IN1 and IN2 and IN3 and IN4;
end Behavioral;
