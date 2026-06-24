-- cnt_4bit_ud.vhd  (4-bit synchronous up/down counter)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity CNT_4BIT_UD is
    Port ( CLK : in  STD_LOGIC;
           RST : in  STD_LOGIC;
           EN  : in  STD_LOGIC;
           DIR : in  STD_LOGIC;  -- '1' = up, '0' = down
           Q0  : out STD_LOGIC;
           Q1  : out STD_LOGIC;
           Q2  : out STD_LOGIC;
           Q3  : out STD_LOGIC;
           TC  : out STD_LOGIC);  -- terminal count
end CNT_4BIT_UD;

architecture Behavioral of CNT_4BIT_UD is
    signal count : unsigned(3 downto 0) := (others => '0');
begin
    process(CLK, RST)
    begin
        if RST = '1' then
            count <= (others => '0');
        elsif rising_edge(CLK) then
            if EN = '1' then
                if DIR = '1' then
                    count <= count + 1;
                else
                    count <= count - 1;
                end if;
            end if;
        end if;
    end process;

    Q0 <= count(0);
    Q1 <= count(1);
    Q2 <= count(2);
    Q3 <= count(3);
    TC <= '1' when (DIR = '1' and count = "1111" and EN = '1') or
                   (DIR = '0' and count = "0000" and EN = '1') else '0';
end Behavioral;
