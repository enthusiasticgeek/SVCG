-- fa_gc.vhd  Full Adder Gray Cell (used in Kogge-Stone / parallel prefix adders)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity FA_GC is
    Port ( A   : in  STD_LOGIC;
           B   : in  STD_LOGIC;
           SI  : in  STD_LOGIC;
           CI  : in  STD_LOGIC;
           SO  : out STD_LOGIC;
           CO  : out STD_LOGIC
         );
end FA_GC;

architecture Behavioral of FA_GC is
    signal G : STD_LOGIC;  -- Generate
    signal P : STD_LOGIC;  -- Propagate
begin
    G  <= A and B;
    P  <= A xor B;
    CO <= G or (P and SI);
    SO <= P xor CI;
end Behavioral;
