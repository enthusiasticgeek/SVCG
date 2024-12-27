-- or.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity OR_GATE is
    Port ( IN1 : in  STD_LOGIC;
           IN2 : in  STD_LOGIC;
           OUT1 : out  STD_LOGIC);
end OR_GATE;

architecture Behavioral of OR_GATE is
begin
    OUT1 <= IN1 or IN2;
end Behavioral;
