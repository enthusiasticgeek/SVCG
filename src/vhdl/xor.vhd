-- xor.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity XOR_GATE is
    Port ( IN1 : in  STD_LOGIC;
           IN2 : in  STD_LOGIC;
           OUT1 : out  STD_LOGIC);
end XOR_GATE;

architecture Behavioral of XOR_GATE is
begin
    OUT1 <= IN1 xor IN2;
end Behavioral;
