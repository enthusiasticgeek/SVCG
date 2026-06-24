-- comp_4bit.vhd  (4-bit magnitude comparator)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity COMP_4BIT is
    Port ( A0  : in  STD_LOGIC;
           A1  : in  STD_LOGIC;
           A2  : in  STD_LOGIC;
           A3  : in  STD_LOGIC;
           B0  : in  STD_LOGIC;
           B1  : in  STD_LOGIC;
           B2  : in  STD_LOGIC;
           B3  : in  STD_LOGIC;
           ALB : out STD_LOGIC;   -- A < B
           AEB : out STD_LOGIC;   -- A = B
           AGB : out STD_LOGIC);  -- A > B
end COMP_4BIT;

architecture Behavioral of COMP_4BIT is
    signal A_vec, B_vec : unsigned(3 downto 0);
begin
    A_vec <= A3 & A2 & A1 & A0;
    B_vec <= B3 & B2 & B1 & B0;

    ALB <= '1' when A_vec < B_vec else '0';
    AEB <= '1' when A_vec = B_vec else '0';
    AGB <= '1' when A_vec > B_vec else '0';
end Behavioral;
