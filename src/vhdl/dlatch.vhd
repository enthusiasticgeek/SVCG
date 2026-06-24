-- dlatch.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity DLATCH is
    Port ( D  : in  STD_LOGIC;
           EN : in  STD_LOGIC;
           Q  : out STD_LOGIC;
           Q_bar : out STD_LOGIC);
end DLATCH;

architecture Behavioral of DLATCH is
    signal Q_internal : STD_LOGIC := '0';
begin
    process(D, EN)
    begin
        if EN = '1' then
            Q_internal <= D;
        end if;
    end process;

    Q     <= Q_internal;
    Q_bar <= not Q_internal;
end Behavioral;
