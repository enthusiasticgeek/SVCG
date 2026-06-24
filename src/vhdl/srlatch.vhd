-- srlatch.vhd  (NOR-based SR latch)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity SRLATCH is
    Port ( S     : in  STD_LOGIC;
           R     : in  STD_LOGIC;
           Q     : out STD_LOGIC;
           Q_bar : out STD_LOGIC);
end SRLATCH;

architecture Behavioral of SRLATCH is
    signal Q_int  : STD_LOGIC := '0';
    signal QB_int : STD_LOGIC := '1';
begin
    Q_int  <= not (R or QB_int);
    QB_int <= not (S or Q_int);

    Q     <= Q_int;
    Q_bar <= QB_int;
end Behavioral;
