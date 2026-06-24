-- xor3.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity XOR3_GATE is
    Port ( IN1  : in  STD_LOGIC;
           IN2  : in  STD_LOGIC;
           IN3  : in  STD_LOGIC;
           OUT1 : out STD_LOGIC);
end XOR3_GATE;

architecture Behavioral of XOR3_GATE is
begin
    OUT1 <= IN1 xor IN2 xor IN3;
end Behavioral;
