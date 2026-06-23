-- mux_4x1.vhd  (select ports S0,S1 as individual STD_LOGIC to match SVCG block)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity MUX4x1 is
    Port ( I0 : in  STD_LOGIC := '0';
           I1 : in  STD_LOGIC := '0';
           I2 : in  STD_LOGIC := '0';
           I3 : in  STD_LOGIC := '0';
           S0 : in  STD_LOGIC := '0';
           S1 : in  STD_LOGIC := '0';
           EN : in  STD_LOGIC := '1';
           O0 : out STD_LOGIC
         );
end MUX4x1;

architecture Behavioral of MUX4x1 is
    signal S : STD_LOGIC_VECTOR(1 downto 0);
begin
    S <= S1 & S0;
    process(I0, I1, I2, I3, S, EN)
    begin
        if EN = '0' then
            O0 <= 'Z';
        else
            case S is
                when "00" => O0 <= I0;
                when "01" => O0 <= I1;
                when "10" => O0 <= I2;
                when "11" => O0 <= I3;
                when others => O0 <= 'Z';
            end case;
        end if;
    end process;
end Behavioral;
