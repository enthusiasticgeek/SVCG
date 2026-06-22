-- fa_wc.vhd  Full Adder White Cell (used in Kogge-Stone / parallel prefix adders)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity FA_WC is
    Port ( A   : in  STD_LOGIC;
           B   : in  STD_LOGIC;
           SI  : in  STD_LOGIC;
           CI  : in  STD_LOGIC;
           SO  : out STD_LOGIC;
           CO  : out STD_LOGIC
         );
end FA_WC;

architecture Behavioral of FA_WC is
    signal P : STD_LOGIC;  -- Propagate
begin
    P  <= A xor B;
    CO <= P and SI;
    SO <= P xor CI;
end Behavioral;
