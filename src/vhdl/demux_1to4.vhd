-- demux_1to4.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity DEMUX_1TO4 is
    Port ( I  : in  STD_LOGIC;
           S0 : in  STD_LOGIC;
           S1 : in  STD_LOGIC;
           EN : in  STD_LOGIC;
           O0 : out STD_LOGIC;
           O1 : out STD_LOGIC;
           O2 : out STD_LOGIC;
           O3 : out STD_LOGIC);
end DEMUX_1TO4;

architecture Behavioral of DEMUX_1TO4 is
begin
    process(I, S0, S1, EN)
    begin
        O0 <= '0'; O1 <= '0'; O2 <= '0'; O3 <= '0';
        if EN = '1' then
            case (S1 & S0) is
                when "00" => O0 <= I;
                when "01" => O1 <= I;
                when "10" => O2 <= I;
                when "11" => O3 <= I;
                when others => null;
            end case;
        end if;
    end process;
end Behavioral;
