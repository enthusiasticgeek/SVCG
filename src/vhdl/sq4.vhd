-- sq4.vhd  (4-bit unsigned squarer)
-- Computes P[7:0] = A[3:0]^2.
-- A squarer is approximately 1.5x cheaper than a general multiplier because
-- the partial product array is symmetric: cross terms ai*aj appear twice
-- (as 2*ai*aj), halving the number of distinct partial products.
-- The behavioural NUMERIC_STD multiplication captures this structure;
-- synthesis tools typically infer a squarer-optimised circuit.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity SQ4 is
    Port ( A0 : in  STD_LOGIC;
           A1 : in  STD_LOGIC;
           A2 : in  STD_LOGIC;
           A3 : in  STD_LOGIC;
           P0 : out STD_LOGIC;
           P1 : out STD_LOGIC;
           P2 : out STD_LOGIC;
           P3 : out STD_LOGIC;
           P4 : out STD_LOGIC;
           P5 : out STD_LOGIC;
           P6 : out STD_LOGIC;
           P7 : out STD_LOGIC);
end SQ4;

architecture Behavioral of SQ4 is
begin
    process(A0, A1, A2, A3)
        variable A_v : unsigned(3 downto 0);
        variable P_v : unsigned(7 downto 0);
    begin
        A_v := unsigned(std_logic_vector'(A3 & A2 & A1 & A0));
        P_v := A_v * A_v;
        P0 <= P_v(0);  P1 <= P_v(1);  P2 <= P_v(2);  P3 <= P_v(3);
        P4 <= P_v(4);  P5 <= P_v(5);  P6 <= P_v(6);  P7 <= P_v(7);
    end process;
end Behavioral;
