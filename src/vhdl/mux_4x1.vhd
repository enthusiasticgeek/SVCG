--mux_4x1
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity MUX4x1 is
    Port ( I0 : in  STD_LOGIC;  -- Input 0
           I1 : in  STD_LOGIC;  -- Input 1
           I2 : in  STD_LOGIC;  -- Input 2
           I3 : in  STD_LOGIC;  -- Input 3
           S  : in  STD_LOGIC_VECTOR(1 downto 0);  -- 2-bit select signal
           EN : in  STD_LOGIC;  -- Enable signal
           O  : out STD_LOGIC   -- Output
         );
end MUX4x1;

architecture Behavioral of MUX4x1 is
begin
    process(I0, I1, I2, I3, S, EN)
    begin
        if (EN = '0') then
            O <= 'Z'; -- High-impedance state
        else
            case S is
                when "00" => O <= I0;
                when "01" => O <= I1;
                when "10" => O <= I2;
                when "11" => O <= I3;
                when others => O <= 'Z'; -- Safety fallback
            end case;
        end if;
    end process;
end Behavioral;
