-- nor.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity NOR_GATE is
    Port ( IN1 : in  STD_LOGIC;
           IN2 : in  STD_LOGIC;
           OUT1 : out  STD_LOGIC);
end NOR_GATE;

architecture Behavioral of NOR_GATE is
begin
    OUT1 <= not (IN1 or IN2);
end Behavioral;
