-- wallace3_4.vhd  (3-operand 4-bit Wallace tree adder)
-- Adds three 4-bit unsigned numbers A + B + C → 6-bit result P[5:0].
-- Stage 1: one CSA (3:2 compressor) layer reduces three 4-bit addends to
--          two: sum vector s[3:0] and carry vector c[3:0].
-- Stage 2: final carry-propagate adder (CPA) computes P = s + (c << 1).
-- Maximum input value: 3 × 15 = 45, which fits in 6 bits.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity WALLACE3_4 is
    Port ( A0 : in  STD_LOGIC;
           A1 : in  STD_LOGIC;
           A2 : in  STD_LOGIC;
           A3 : in  STD_LOGIC;
           B0 : in  STD_LOGIC;
           B1 : in  STD_LOGIC;
           B2 : in  STD_LOGIC;
           B3 : in  STD_LOGIC;
           C0 : in  STD_LOGIC;
           C1 : in  STD_LOGIC;
           C2 : in  STD_LOGIC;
           C3 : in  STD_LOGIC;
           P0 : out STD_LOGIC;
           P1 : out STD_LOGIC;
           P2 : out STD_LOGIC;
           P3 : out STD_LOGIC;
           P4 : out STD_LOGIC;
           P5 : out STD_LOGIC);
end WALLACE3_4;

architecture Structural of WALLACE3_4 is
    -- CSA outputs: s[i] stays at bit i, co[i] carries to bit i+1
    signal s0, s1, s2, s3   : STD_LOGIC;
    signal co0, co1, co2, co3 : STD_LOGIC;
    -- Final CPA carry chain
    signal cc1, cc2, cc3, cc4 : STD_LOGIC;
begin
    -- ── CSA stage (3:2 compressor for each bit) ───────────────────────────────
    s0  <= A0 xor B0 xor C0;  co0 <= (A0 and B0) or (A0 and C0) or (B0 and C0);
    s1  <= A1 xor B1 xor C1;  co1 <= (A1 and B1) or (A1 and C1) or (B1 and C1);
    s2  <= A2 xor B2 xor C2;  co2 <= (A2 and B2) or (A2 and C2) or (B2 and C2);
    s3  <= A3 xor B3 xor C3;  co3 <= (A3 and B3) or (A3 and C3) or (B3 and C3);

    -- ── Final CPA: add {0, s3, s2, s1, s0} + {co3, co2, co1, co0, 0} ─────────
    -- Bit 0: only s0, no co contribution
    P0   <= s0;

    -- Bit 1: HA(s1, co0)
    P1   <= s1 xor co0;
    cc1  <= s1 and co0;

    -- Bit 2: FA(s2, co1, cc1)
    P2   <= s2 xor co1 xor cc1;
    cc2  <= (s2 and co1) or (s2 and cc1) or (co1 and cc1);

    -- Bit 3: FA(s3, co2, cc2)
    P3   <= s3 xor co2 xor cc2;
    cc3  <= (s3 and co2) or (s3 and cc2) or (co2 and cc2);

    -- Bit 4: HA(co3, cc3)
    P4   <= co3 xor cc3;
    cc4  <= co3 and cc3;

    -- Bit 5: final carry
    P5   <= cc4;
end Structural;
