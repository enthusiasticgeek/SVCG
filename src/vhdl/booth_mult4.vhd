-- booth_mult4.vhd  (4-bit signed Booth multiplier, radix-2)
-- Implements the Booth recoding algorithm explicitly:
--   examine (Q[i], Q[i-1]) pairs from LSB to MSB with Q[-1]=0
--   00 or 11 -> add 0 (no operation)
--   01       -> add multiplicand A
--   10       -> subtract multiplicand A (add two's complement)
-- Accumulation is done in 9-bit arithmetic to preserve sign extension.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity BOOTH_MULT4 is
    Port ( A0 : in  STD_LOGIC;  -- multiplicand (signed, LSB first)
           A1 : in  STD_LOGIC;
           A2 : in  STD_LOGIC;
           A3 : in  STD_LOGIC;
           B0 : in  STD_LOGIC;  -- multiplier (signed, LSB first)
           B1 : in  STD_LOGIC;
           B2 : in  STD_LOGIC;
           B3 : in  STD_LOGIC;
           P0 : out STD_LOGIC;  -- 8-bit signed product
           P1 : out STD_LOGIC;
           P2 : out STD_LOGIC;
           P3 : out STD_LOGIC;
           P4 : out STD_LOGIC;
           P5 : out STD_LOGIC;
           P6 : out STD_LOGIC;
           P7 : out STD_LOGIC);
end BOOTH_MULT4;

architecture Behavioral of BOOTH_MULT4 is
begin
    process(A0, A1, A2, A3, B0, B1, B2, B3)
        variable A_v    : signed(3 downto 0);
        variable B_v    : signed(4 downto 0);  -- B extended with Q[-1]=0
        variable acc    : signed(8 downto 0);
        variable add_v  : signed(8 downto 0);
        variable qi, qi1 : std_logic;
    begin
        A_v := signed(std_logic_vector'(A3 & A2 & A1 & A0));
        -- Append implicit Q[-1]=0 at position -1 (stored as LSB of B_v)
        B_v := signed(std_logic_vector'(B3 & B2 & B1 & B0 & '0'));
        acc := (others => '0');

        -- 4 Booth steps, each examining (B[i], B[i-1])
        for i in 0 to 3 loop
            qi  := B_v(i + 1);   -- current multiplier bit
            qi1 := B_v(i);       -- previous bit (B[-1]=0 for i=0)
            if qi = '0' and qi1 = '1' then
                -- add sign-extended A shifted left by i
                add_v := resize(shift_left(resize(A_v, 9), i), 9);
                acc   := acc + add_v;
            elsif qi = '1' and qi1 = '0' then
                -- subtract sign-extended A shifted left by i
                add_v := resize(shift_left(resize(A_v, 9), i), 9);
                acc   := acc - add_v;
            end if;
            -- 00 or 11: no operation
        end loop;

        P0 <= acc(0);
        P1 <= acc(1);
        P2 <= acc(2);
        P3 <= acc(3);
        P4 <= acc(4);
        P5 <= acc(5);
        P6 <= acc(6);
        P7 <= acc(7);
    end process;
end Behavioral;
