-- shreg_4bit.vhd  (4-bit serial-in parallel-out shift register)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity SHREG_4BIT is
    Port ( SIN : in  STD_LOGIC;
           CLK : in  STD_LOGIC;
           RST : in  STD_LOGIC;
           Q0  : out STD_LOGIC;
           Q1  : out STD_LOGIC;
           Q2  : out STD_LOGIC;
           Q3  : out STD_LOGIC);
end SHREG_4BIT;

architecture Behavioral of SHREG_4BIT is
    signal reg : STD_LOGIC_VECTOR(3 downto 0) := (others => '0');
begin
    process(CLK, RST)
    begin
        if RST = '1' then
            reg <= (others => '0');
        elsif rising_edge(CLK) then
            reg <= reg(2 downto 0) & SIN;
        end if;
    end process;

    Q0 <= reg(0);
    Q1 <= reg(1);
    Q2 <= reg(2);
    Q3 <= reg(3);
end Behavioral;
