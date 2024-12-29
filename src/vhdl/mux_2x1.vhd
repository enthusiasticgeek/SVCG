--mux_2x1.vhd
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity MUX2x1 is
    Port ( I0 : in  STD_LOGIC;  -- Input 0
           I1 : in  STD_LOGIC;  -- Input 1
           S0 : in  STD_LOGIC;  -- Select signal
           EN : in  STD_LOGIC;  -- Enable signal (controls high-impedance state)
           O0 : out STD_LOGIC   -- Output
         );
end MUX2x1;

architecture Behavioral of MUX2x1 is
begin
    process(I0, I1, S0, EN)
    begin
        if (EN = '0') then
            O0 <= 'Z'; -- High-impedance state
        else
            -- Multiplexer logic
            if (S0 = '0') then
                O0 <= I0; -- Select input I0
            else
                O0 <= I1; -- Select input I1
            end if;
        end if;
    end process;
end Behavioral;
