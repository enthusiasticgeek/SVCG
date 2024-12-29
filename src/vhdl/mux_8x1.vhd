--mux_8x1
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity MUX8x1 is
    Port ( I0 : in  STD_LOGIC;  -- Input 0
           I1 : in  STD_LOGIC;  -- Input 1
           I2 : in  STD_LOGIC;  -- Input 2
           I3 : in  STD_LOGIC;  -- Input 3
           I4 : in  STD_LOGIC;  -- Input 4
           I5 : in  STD_LOGIC;  -- Input 5
           I6 : in  STD_LOGIC;  -- Input 6
           I7 : in  STD_LOGIC;  -- Input 7
           S  : in  STD_LOGIC_VECTOR(2 downto 0);  -- 3-bit select signal
           EN : in  STD_LOGIC;  -- Enable signal
           O  : out STD_LOGIC   -- Output
         );
end MUX8x1;

architecture Behavioral of MUX8x1 is
begin
    process(I0, I1, I2, I3, I4, I5, I6, I7, S, EN)
    begin
        if (EN = '0') then
            O <= 'Z'; -- High-impedance state
        else
            case S is
                when "000" => O <= I0;
                when "001" => O <= I1;
                when "010" => O <= I2;
                when "011" => O <= I3;
                when "100" => O <= I4;
                when "101" => O <= I5;
                when "110" => O <= I6;
                when "111" => O <= I7;
                when others => O <= 'Z'; -- Safety fallback
            end case;
        end if;
    end process;
end Behavioral;
