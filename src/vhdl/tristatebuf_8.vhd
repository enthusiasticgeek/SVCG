--tristatebuf_8
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity TristateBuffer8 is
    Port ( I0 : in  STD_LOGIC;  -- Input 0
           I1 : in  STD_LOGIC;  -- Input 1
           I2 : in  STD_LOGIC;  -- Input 2
           I3 : in  STD_LOGIC;  -- Input 3
           I4 : in  STD_LOGIC;  -- Input 4
           I5 : in  STD_LOGIC;  -- Input 5
           I6 : in  STD_LOGIC;  -- Input 6
           I7 : in  STD_LOGIC;  -- Input 7
           EN : in  STD_LOGIC;  -- Enable signal
           O0 : out STD_LOGIC;  -- Output 0
           O1 : out STD_LOGIC;  -- Output 1
           O2 : out STD_LOGIC;  -- Output 2
           O3 : out STD_LOGIC;  -- Output 3
           O4 : out STD_LOGIC;  -- Output 4
           O5 : out STD_LOGIC;  -- Output 5
           O6 : out STD_LOGIC;  -- Output 6
           O7 : out STD_LOGIC   -- Output 7
         );
end TristateBuffer8;

architecture Behavioral of TristateBuffer8 is
begin
    process(I0, I1, I2, I3, I4, I5, I6, I7, EN)
    begin
        if (EN = '1') then
            -- Enable outputs
            O0 <= I0;
            O1 <= I1;
            O2 <= I2;
            O3 <= I3;
            O4 <= I4;
            O5 <= I5;
            O6 <= I6;
            O7 <= I7;
        else
            -- High-impedance state
            O0 <= 'Z';
            O1 <= 'Z';
            O2 <= 'Z';
            O3 <= 'Z';
            O4 <= 'Z';
            O5 <= 'Z';
            O6 <= 'Z';
            O7 <= 'Z';
        end if;
    end process;
end Behavioral;

