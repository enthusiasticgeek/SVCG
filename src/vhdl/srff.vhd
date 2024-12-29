--srff.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity SRFF is
    Port ( S   : in  STD_LOGIC;
           CLK : in  STD_LOGIC;
           R   : in  STD_LOGIC;
           PRE : in  STD_LOGIC;
           CLR : in  STD_LOGIC;
           Q   : out STD_LOGIC;
           Q_bar : out STD_LOGIC );
end SRFF;

architecture Behavioral of SRFF is
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
            -- SR flip-flop behavior
            if (S = '1' and R = '0') then
                Q_internal <= '1'; -- Set
            elsif (S = '0' and R = '1') then
                Q_internal <= '0'; -- Reset
            elsif (S = '1' and R = '1') then
                Q_internal <= 'X'; -- Invalid state
            end if;
        end if;
    end process;

    -- Assign outputs
    Q <= Q_internal;
    Q_bar <= not Q_internal;

end Behavioral;
