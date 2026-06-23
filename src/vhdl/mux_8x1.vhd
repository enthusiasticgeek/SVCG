-- mux_8x1.vhd  (select ports S0,S1,S2 as individual STD_LOGIC to match SVCG block)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity MUX8x1 is
    Port ( I0 : in  STD_LOGIC := '0';
           I1 : in  STD_LOGIC := '0';
           I2 : in  STD_LOGIC := '0';
           I3 : in  STD_LOGIC := '0';
           I4 : in  STD_LOGIC := '0';
           I5 : in  STD_LOGIC := '0';
           I6 : in  STD_LOGIC := '0';
           I7 : in  STD_LOGIC := '0';
           S0 : in  STD_LOGIC := '0';
           S1 : in  STD_LOGIC := '0';
           S2 : in  STD_LOGIC := '0';
           EN : in  STD_LOGIC := '1';
           O0 : out STD_LOGIC
         );
end MUX8x1;

architecture Behavioral of MUX8x1 is
    signal S : STD_LOGIC_VECTOR(2 downto 0);
begin
    S <= S2 & S1 & S0;
    process(I0, I1, I2, I3, I4, I5, I6, I7, S, EN)
    begin
        if EN = '0' then
            O0 <= 'Z';
        else
            case S is
                when "000" => O0 <= I0;
                when "001" => O0 <= I1;
                when "010" => O0 <= I2;
                when "011" => O0 <= I3;
                when "100" => O0 <= I4;
                when "101" => O0 <= I5;
                when "110" => O0 <= I6;
                when "111" => O0 <= I7;
                when others => O0 <= 'Z';
            end case;
        end if;
    end process;
end Behavioral;
