-- fa.vhd  Full Adder
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity FA is
    Port ( A   : in  STD_LOGIC;
           B   : in  STD_LOGIC;
           SI  : in  STD_LOGIC;  -- Carry in
           CI  : in  STD_LOGIC;  -- Serial/pipeline input
           SO  : out STD_LOGIC;  -- Sum out
           CO  : out STD_LOGIC   -- Carry out
         );
end FA;

architecture Behavioral of FA is
begin
    SO <= A xor B xor SI;
    CO <= (A and B) or (SI and (A xor B));
end Behavioral;
