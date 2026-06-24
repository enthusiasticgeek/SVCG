-- demux_1to8.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity DEMUX_1TO8 is
    Port ( I  : in  STD_LOGIC;
           S0 : in  STD_LOGIC;
           S1 : in  STD_LOGIC;
           S2 : in  STD_LOGIC;
           EN : in  STD_LOGIC;
           O0 : out STD_LOGIC;
           O1 : out STD_LOGIC;
           O2 : out STD_LOGIC;
           O3 : out STD_LOGIC;
           O4 : out STD_LOGIC;
           O5 : out STD_LOGIC;
           O6 : out STD_LOGIC;
           O7 : out STD_LOGIC);
end DEMUX_1TO8;

architecture Behavioral of DEMUX_1TO8 is
begin
    process(I, S0, S1, S2, EN)
    begin
        O0<='0'; O1<='0'; O2<='0'; O3<='0';
        O4<='0'; O5<='0'; O6<='0'; O7<='0';
        if EN = '1' then
            case (S2 & S1 & S0) is
                when "000" => O0 <= I;
                when "001" => O1 <= I;
                when "010" => O2 <= I;
                when "011" => O3 <= I;
                when "100" => O4 <= I;
                when "101" => O5 <= I;
                when "110" => O6 <= I;
                when "111" => O7 <= I;
                when others => null;
            end case;
        end if;
    end process;
end Behavioral;
