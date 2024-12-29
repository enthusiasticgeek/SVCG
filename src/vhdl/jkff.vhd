--jkff.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity JKFF is
    Port ( J   : in  STD_LOGIC;
           CLK : in  STD_LOGIC;
           K   : in  STD_LOGIC;
           PRE : in  STD_LOGIC;
           CLR : in  STD_LOGIC;
           Q   : out STD_LOGIC;
           Q_bar : out STD_LOGIC );
end JKFF;

architecture Behavioral of JKFF is
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
            -- JK flip-flop behavior
            case (J & K) is
                when "00" => 
                    -- No change
                    Q_internal <= Q_internal;
                when "01" =>
                    -- Reset
                    Q_internal <= '0';
                when "10" =>
                    -- Set
                    Q_internal <= '1';
                when "11" =>
                    -- Toggle
                    Q_internal <= not Q_internal;
                when others =>
                    -- Default case
                    Q_internal <= Q_internal;
            end case;
        end if;
    end process;

    -- Assign outputs
    Q <= Q_internal;
    Q_bar <= not Q_internal;

end Behavioral;
