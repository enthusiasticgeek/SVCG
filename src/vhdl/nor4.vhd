-- nor4.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity NOR4_GATE is
    Port ( IN1  : in  STD_LOGIC;
           IN2  : in  STD_LOGIC;
           IN3  : in  STD_LOGIC;
           IN4  : in  STD_LOGIC;
           OUT1 : out STD_LOGIC);
end NOR4_GATE;

architecture Behavioral of NOR4_GATE is
begin
    OUT1 <= not (IN1 or IN2 or IN3 or IN4);
end Behavioral;
