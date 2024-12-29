--dff.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity DFF is
    Port ( D   : in  STD_LOGIC;
           CLK : in  STD_LOGIC;
           PRE : in  STD_LOGIC;
           CLR : in  STD_LOGIC;
           Q   : out STD_LOGIC;
           Q_bar : out STD_LOGIC );
end DFF;

architecture Behavioral of DFF is
    signal Q_internal : STD_LOGIC := '0';
begin

    process(CLK, PRE, CLR)
    begin
        -- Asynchronous preset and clear
        if (PRE = '0') then
            Q_internal <= '1';
        elsif (CLR = '0') then
            Q_internal <= '0';
        elsif rising_edge(CLK) then
            -- D Flip-Flop behavior
            Q_internal <= D; -- Follow the input D
        end if;
    end process;

    -- Assign outputs
    Q <= Q_internal;
    Q_bar <= not Q_internal;

end Behavioral;
