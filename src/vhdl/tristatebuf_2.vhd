--tristatebuf_2
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity TristateBuffer is
    Port ( I0 : in  STD_LOGIC;  -- Input 0
           I1 : in  STD_LOGIC;  -- Input 1
           EN : in  STD_LOGIC;  -- Enable signal
           O0 : out STD_LOGIC;  -- Output 0
           O1 : out STD_LOGIC   -- Output 1
         );
end TristateBuffer;

architecture Behavioral of TristateBuffer is
begin
    process(I0, I1, EN)
    begin
        if (EN = '1') then
            -- Enable outputs
            O0 <= I0;
            O1 <= I1;
        else
            -- High-impedance state
            O0 <= 'Z';
            O1 <= 'Z';
        end if;
    end process;
end Behavioral;
