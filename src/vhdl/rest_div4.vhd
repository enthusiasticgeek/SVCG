-- rest_div4.vhd  (4-bit unsigned restoring divider)
-- Classical restoring division algorithm:
--   Maintain a 5-bit partial remainder P (sign bit used to detect underflow).
--   Each iteration: shift P left and bring in next dividend bit,
--   trial-subtract the divisor; if result is negative (borrow), restore P
--   and set quotient bit to 0, otherwise keep result and set bit to 1.
-- Inputs:  N (dividend), D (divisor), each 4 bits, LSB-first.
-- Outputs: Q (quotient), R (remainder), each 4 bits, LSB-first.
-- Division by zero: quotient and remainder are both 0xF (undefined).
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity REST_DIV4 is
    Port ( N0 : in  STD_LOGIC;  -- dividend bits (LSB first)
           N1 : in  STD_LOGIC;
           N2 : in  STD_LOGIC;
           N3 : in  STD_LOGIC;
           D0 : in  STD_LOGIC;  -- divisor bits (LSB first)
           D1 : in  STD_LOGIC;
           D2 : in  STD_LOGIC;
           D3 : in  STD_LOGIC;
           Q0 : out STD_LOGIC;  -- quotient bits (LSB first)
           Q1 : out STD_LOGIC;
           Q2 : out STD_LOGIC;
           Q3 : out STD_LOGIC;
           R0 : out STD_LOGIC;  -- remainder bits (LSB first)
           R1 : out STD_LOGIC;
           R2 : out STD_LOGIC;
           R3 : out STD_LOGIC);
end REST_DIV4;

architecture Behavioral of REST_DIV4 is
begin
    process(N0, N1, N2, N3, D0, D1, D2, D3)
        variable N_v    : unsigned(3 downto 0);
        variable D_v    : unsigned(3 downto 0);
        variable Q_v    : unsigned(3 downto 0);
        variable P      : unsigned(4 downto 0);  -- 5-bit: sign + 4-bit partial rem
        variable trial  : unsigned(4 downto 0);
    begin
        N_v := unsigned(std_logic_vector'(N3 & N2 & N1 & N0));
        D_v := unsigned(std_logic_vector'(D3 & D2 & D1 & D0));
        Q_v := (others => '0');
        P   := (others => '0');

        -- 4 iterations (one per quotient bit), MSB first
        for i in 3 downto 0 loop
            -- Shift P left and bring in next dividend bit
            P := P(3 downto 0) & N_v(i);
            -- Trial subtraction: P - D (in 5-bit arithmetic)
            trial := P - ("0" & D_v);
            if trial(4) = '0' then
                -- No borrow: P >= D, quotient bit = 1
                Q_v(i) := '1';
                P       := trial;
            -- else: borrow, quotient bit = 0, restore P (do nothing)
            end if;
        end loop;

        Q0 <= Q_v(0);  Q1 <= Q_v(1);  Q2 <= Q_v(2);  Q3 <= Q_v(3);
        R0 <= P(0);    R1 <= P(1);    R2 <= P(2);    R3 <= P(3);
    end process;
end Behavioral;
