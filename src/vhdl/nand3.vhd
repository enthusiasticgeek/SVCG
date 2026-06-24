-- nand3.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity NAND3_GATE is
    Port ( IN1  : in  STD_LOGIC;
           IN2  : in  STD_LOGIC;
           IN3  : in  STD_LOGIC;
           OUT1 : out STD_LOGIC);
end NAND3_GATE;

architecture Behavioral of NAND3_GATE is
begin
    OUT1 <= not (IN1 and IN2 and IN3);
end Behavioral;
