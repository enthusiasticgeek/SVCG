-- mod_add4.vhd  (4-bit modular adder)
-- Computes R = (A + B) mod M for unsigned 4-bit operands.
-- Algorithm: S = A + B (5-bit); T = S - M; if T >= 0 then R = T else R = S.
-- Used in GF(p) arithmetic and digital signal processing applications.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity MOD_ADD4 is
    Port ( A0 : in  STD_LOGIC;
           A1 : in  STD_LOGIC;
           A2 : in  STD_LOGIC;
           A3 : in  STD_LOGIC;
           B0 : in  STD_LOGIC;
           B1 : in  STD_LOGIC;
           B2 : in  STD_LOGIC;
           B3 : in  STD_LOGIC;
           M0 : in  STD_LOGIC;
           M1 : in  STD_LOGIC;
           M2 : in  STD_LOGIC;
           M3 : in  STD_LOGIC;
           R0 : out STD_LOGIC;
           R1 : out STD_LOGIC;
           R2 : out STD_LOGIC;
           R3 : out STD_LOGIC);
end MOD_ADD4;

architecture Behavioral of MOD_ADD4 is
begin
    process(A0, A1, A2, A3, B0, B1, B2, B3, M0, M1, M2, M3)
        variable A_v, B_v, M_v : unsigned(4 downto 0);
        variable S_v, T_v, R_v : unsigned(4 downto 0);
    begin
        A_v := '0' & unsigned(std_logic_vector'(A3 & A2 & A1 & A0));
        B_v := '0' & unsigned(std_logic_vector'(B3 & B2 & B1 & B0));
        M_v := '0' & unsigned(std_logic_vector'(M3 & M2 & M1 & M0));

        S_v := A_v + B_v;       -- 5-bit sum
        T_v := S_v - M_v;       -- trial subtract

        if T_v(4) = '0' then    -- no borrow: S >= M
            R_v := T_v;
        else
            R_v := S_v;
        end if;

        R0 <= R_v(0);  R1 <= R_v(1);  R2 <= R_v(2);  R3 <= R_v(3);
    end process;
end Behavioral;
