-- rca_4bit.vhd  (4-bit ripple carry adder)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity RCA_4BIT is
    Port ( A0   : in  STD_LOGIC;
           A1   : in  STD_LOGIC;
           A2   : in  STD_LOGIC;
           A3   : in  STD_LOGIC;
           B0   : in  STD_LOGIC;
           B1   : in  STD_LOGIC;
           B2   : in  STD_LOGIC;
           B3   : in  STD_LOGIC;
           CIN  : in  STD_LOGIC;
           S0   : out STD_LOGIC;
           S1   : out STD_LOGIC;
           S2   : out STD_LOGIC;
           S3   : out STD_LOGIC;
           COUT : out STD_LOGIC);
end RCA_4BIT;

architecture Behavioral of RCA_4BIT is
    signal c1, c2, c3 : STD_LOGIC;
begin
    S0   <= A0 xor B0 xor CIN;
    c1   <= (A0 and B0) or (A0 and CIN) or (B0 and CIN);
    S1   <= A1 xor B1 xor c1;
    c2   <= (A1 and B1) or (A1 and c1) or (B1 and c1);
    S2   <= A2 xor B2 xor c2;
    c3   <= (A2 and B2) or (A2 and c2) or (B2 and c2);
    S3   <= A3 xor B3 xor c3;
    COUT <= (A3 and B3) or (A3 and c3) or (B3 and c3);
end Behavioral;
