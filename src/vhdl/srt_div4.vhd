-- srt_div4.vhd  (4-bit unsigned SRT radix-2 divider)
-- SRT (Sweeney-Robertson-Tocher) radix-2: quotient digit in {-1, 0, +1}.
-- Digit selection: use top bits of partial remainder relative to D.
--   if P >= D/2  (P[5..4] >= 0 and 2P >= D): digit = +1, P := 2P - D
--   if P <= -D/2 (P negative and 2P+D < 0):  digit = -1, P := 2P + D
--   else:                                     digit =  0, P := 2P
-- Stored as (q_pos, q_neg) pairs; binary quotient = q_pos - q_neg at end.
-- Post-correction if final P < 0.
-- Inputs:  N3..N0 (dividend), D3..D0 (divisor), both 4-bit unsigned.
-- Outputs: Q3..Q0 (quotient), R3..R0 (remainder).
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity SRT_DIV4 is
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
end SRT_DIV4;

architecture Behavioral of SRT_DIV4 is
begin
    process(N0,N1,N2,N3,D0,D1,D2,D3)
        variable N_v   : unsigned(3 downto 0);
        variable D_v   : unsigned(3 downto 0);
        variable D_s   : signed(5 downto 0);
        variable P     : signed(5 downto 0);
        variable twoP  : signed(5 downto 0);
        variable q_pos : unsigned(3 downto 0);
        variable q_neg : unsigned(3 downto 0);
        variable Q_v   : unsigned(3 downto 0);
    begin
        N_v   := unsigned(std_logic_vector'(N3 & N2 & N1 & N0));
        D_v   := unsigned(std_logic_vector'(D3 & D2 & D1 & D0));
        D_s   := signed("00" & std_logic_vector(D_v));
        P     := (others => '0');
        q_pos := (others => '0');
        q_neg := (others => '0');

        for i in 3 downto 0 loop
            -- Shift P left and bring in next dividend bit
            P := signed(std_logic_vector(P(4 downto 0)) & N_v(i));
            twoP := P;   -- already shifted

            -- SRT digit selection
            if twoP >= D_s then          -- digit = +1
                P        := twoP - D_s;
                q_pos(i) := '1';
            elsif twoP <= -D_s then      -- digit = -1
                P        := twoP + D_s;
                q_neg(i) := '1';
            end if;
            -- else digit = 0: P stays as twoP
        end loop;

        -- Convert signed-digit quotient: Q = q_pos - q_neg
        Q_v := q_pos - q_neg;

        -- Post-correction if remainder negative
        if P(5) = '1' then
            P   := P + D_s;
            Q_v := Q_v - 1;
        end if;

        Q0 <= Q_v(0);  Q1 <= Q_v(1);  Q2 <= Q_v(2);  Q3 <= Q_v(3);
        R0 <= P(0);    R1 <= P(1);    R2 <= P(2);    R3 <= P(3);
    end process;
end Behavioral;
