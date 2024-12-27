-- xnor.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity XNOR_GATE is
    Port ( IN1 : in  STD_LOGIC;
           IN2 : in  STD_LOGIC;
           OUT1 : out  STD_LOGIC);
end XNOR_GATE;

architecture Behavioral of XNOR_GATE is
begin
    OUT1 <= not (IN1 xor IN2);
end Behavioral;
