-- nonrest_div4.vhd  (4-bit unsigned non-restoring divider)
-- Non-restoring division avoids the restore step when P goes negative:
--   if P >= 0: subtract D  (quotient digit = +1)
--   if P <  0: add D       (quotient digit = -1, stored as 0)
-- The quotient is in signed-digit {+1,-1} form.  After the loop the
-- binary quotient is recovered as Q^+ - Q^- and then post-corrected
-- if the final partial remainder is still negative.
-- Inputs:  N (dividend), D (divisor), LSB-first 4-bit unsigned.
-- Outputs: Q (quotient), R (remainder), LSB-first 4-bit unsigned.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity NONREST_DIV4 is
    Port ( N0 : in  STD_LOGIC;
           N1 : in  STD_LOGIC;
           N2 : in  STD_LOGIC;
           N3 : in  STD_LOGIC;
           D0 : in  STD_LOGIC;
           D1 : in  STD_LOGIC;
           D2 : in  STD_LOGIC;
           D3 : in  STD_LOGIC;
           Q0 : out STD_LOGIC;
           Q1 : out STD_LOGIC;
           Q2 : out STD_LOGIC;
           Q3 : out STD_LOGIC;
           R0 : out STD_LOGIC;
           R1 : out STD_LOGIC;
           R2 : out STD_LOGIC;
           R3 : out STD_LOGIC);
end NONREST_DIV4;

architecture Behavioral of NONREST_DIV4 is
begin
    process(N0, N1, N2, N3, D0, D1, D2, D3)
        variable N_v  : unsigned(3 downto 0);
        variable D_v  : unsigned(3 downto 0);
        variable D_s  : signed(5 downto 0);   -- zero-extended divisor
        variable P    : signed(5 downto 0);   -- 6-bit: handles |P| <= 2D without overflow
        variable qbits: unsigned(3 downto 0); -- 1=positive digit, 0=negative digit
        variable q_pos: unsigned(3 downto 0);
        variable q_neg: unsigned(3 downto 0);
        variable Q_v  : unsigned(3 downto 0);
    begin
        N_v  := unsigned(std_logic_vector'(N3 & N2 & N1 & N0));
        D_v  := unsigned(std_logic_vector'(D3 & D2 & D1 & D0));
        D_s  := signed("00" & std_logic_vector(D_v));
        P    := (others => '0');
        qbits := (others => '0');

        -- Non-restoring loop: process each dividend bit MSB-first
        for i in 3 downto 0 loop
            -- Shift P left and bring in next dividend bit (6-bit, keeps sign correct)
            P := signed(std_logic_vector(P(4 downto 0)) & N_v(i));
            if P(5) = '0' then          -- P >= 0: subtract D
                P       := P - D_s;
                qbits(i) := '1';        -- quotient digit = +1
            else                        -- P < 0: add D (no restore)
                P       := P + D_s;
                qbits(i) := '0';        -- quotient digit = -1
            end if;
        end loop;

        -- Convert signed-digit quotient to unsigned binary: Q = Q^+ - Q^-
        q_pos := qbits;
        q_neg := not qbits;
        Q_v   := q_pos - q_neg;

        -- Post-correction: if remainder still negative, R += D, Q -= 1
        if P(5) = '1' then
            P   := P + D_s;
            Q_v := Q_v - 1;
        end if;

        Q0 <= Q_v(0);  Q1 <= Q_v(1);  Q2 <= Q_v(2);  Q3 <= Q_v(3);
        R0 <= P(0);    R1 <= P(1);    R2 <= P(2);    R3 <= P(3);
    end process;
end Behavioral;
