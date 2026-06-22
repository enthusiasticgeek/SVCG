-- ha.vhd  Half Adder
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity HA is
    Port ( A  : in  STD_LOGIC;
           B  : in  STD_LOGIC;
           SO : out STD_LOGIC;  -- Sum
           CO : out STD_LOGIC   -- Carry out
         );
end HA;

architecture Behavioral of HA is
begin
    SO <= A xor B;
    CO <= A and B;
end Behavioral;
