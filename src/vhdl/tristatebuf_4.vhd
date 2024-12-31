--tristatebuf_4
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity TristateBuffer4 is
    Port ( I0 : in  STD_LOGIC;  -- Input 0
           I1 : in  STD_LOGIC;  -- Input 1
           I2 : in  STD_LOGIC;  -- Input 2
           I3 : in  STD_LOGIC;  -- Input 3
           EN : in  STD_LOGIC;  -- Enable signal
           O0 : out STD_LOGIC;  -- Output 0
           O1 : out STD_LOGIC;  -- Output 1
           O2 : out STD_LOGIC;  -- Output 2
           O3 : out STD_LOGIC   -- Output 3
         );
end TristateBuffer4;

architecture Behavioral of TristateBuffer4 is
begin
    process(I0, I1, I2, I3, EN)
    begin
        if (EN = '1') then
            -- Enable outputs
            O0 <= I0;
            O1 <= I1;
            O2 <= I2;
            O3 <= I3;
        else
            -- High-impedance state
            O0 <= 'Z';
            O1 <= 'Z';
            O2 <= 'Z';
            O3 <= 'Z';
        end if;
    end process;
end Behavioral;
