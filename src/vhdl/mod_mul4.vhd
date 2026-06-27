-- mod_mul4.vhd  (4-bit modular multiplier)
-- Computes R = (A * B) mod M using shift-and-add with modular reduction.
-- A, B, M are 4-bit unsigned; result R is 4-bit.
-- Uses an 8-bit accumulator to hold intermediate A*B before reduction.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity MOD_MUL4 is
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
end MOD_MUL4;

architecture Behavioral of MOD_MUL4 is
begin
    process(A0,A1,A2,A3,B0,B1,B2,B3,M0,M1,M2,M3)
        variable A_v : unsigned(3 downto 0);
        variable B_v : unsigned(3 downto 0);
        variable M_v : unsigned(3 downto 0);
        variable P_v : unsigned(7 downto 0);   -- full 8-bit product
        variable R_v : unsigned(7 downto 0);   -- remainder (extended)
    begin
        A_v := unsigned(std_logic_vector'(A3 & A2 & A1 & A0));
        B_v := unsigned(std_logic_vector'(B3 & B2 & B1 & B0));
        M_v := unsigned(std_logic_vector'(M3 & M2 & M1 & M0));

        P_v := A_v * B_v;   -- 8-bit product

        -- Reduce mod M; guard against M=0 to avoid infinite loop
        if M_v = 0 then
            R_v := P_v;
        else
            R_v := P_v;
            while R_v >= ("0000" & M_v) loop
                R_v := R_v - ("0000" & M_v);
            end loop;
        end if;

        R0 <= R_v(0);  R1 <= R_v(1);  R2 <= R_v(2);  R3 <= R_v(3);
    end process;
end Behavioral;
