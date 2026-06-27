-- array_mult4.vhd  (4x4 unsigned array multiplier)
-- Generates all 16 partial products (AND array) and reduces them with
-- a cascade of half adders and full adders, mimicking the gate-level
-- structure of a classical array multiplier.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ARRAY_MULT4 is
    Port ( A0 : in  STD_LOGIC;
           A1 : in  STD_LOGIC;
           A2 : in  STD_LOGIC;
           A3 : in  STD_LOGIC;
           B0 : in  STD_LOGIC;
           B1 : in  STD_LOGIC;
           B2 : in  STD_LOGIC;
           B3 : in  STD_LOGIC;
           P0 : out STD_LOGIC;
           P1 : out STD_LOGIC;
           P2 : out STD_LOGIC;
           P3 : out STD_LOGIC;
           P4 : out STD_LOGIC;
           P5 : out STD_LOGIC;
           P6 : out STD_LOGIC;
           P7 : out STD_LOGIC);
end ARRAY_MULT4;

architecture Structural of ARRAY_MULT4 is
    -- Partial products: pp[i][j] = Ai AND Bj
    signal pp00, pp10, pp20, pp30 : STD_LOGIC;  -- B0 row
    signal pp01, pp11, pp21, pp31 : STD_LOGIC;  -- B1 row
    signal pp02, pp12, pp22, pp32 : STD_LOGIC;  -- B2 row
    signal pp03, pp13, pp23, pp33 : STD_LOGIC;  -- B3 row

    -- Row 1 adder outputs (HA + FA chain)
    signal r1s1, r1c1 : STD_LOGIC;   -- bit 1
    signal r1s2, r1c2 : STD_LOGIC;   -- bit 2
    signal r1s3, r1c3 : STD_LOGIC;   -- bit 3
    signal r1s4, r1c4 : STD_LOGIC;   -- bit 4 (overflow into bit 5)

    -- Row 2 adder outputs
    signal r2s2, r2c2 : STD_LOGIC;
    signal r2s3, r2c3 : STD_LOGIC;
    signal r2s4, r2c4 : STD_LOGIC;
    signal r2s5, r2c5 : STD_LOGIC;

    -- Row 3 adder outputs
    signal r3s3, r3c3 : STD_LOGIC;
    signal r3s4, r3c4 : STD_LOGIC;
    signal r3s5, r3c5 : STD_LOGIC;
    signal r3s6, r3c6 : STD_LOGIC;

begin
    -- ── Partial product generation ────────────────────────────────────────────
    pp00 <= A0 and B0;  pp10 <= A1 and B0;  pp20 <= A2 and B0;  pp30 <= A3 and B0;
    pp01 <= A0 and B1;  pp11 <= A1 and B1;  pp21 <= A2 and B1;  pp31 <= A3 and B1;
    pp02 <= A0 and B2;  pp12 <= A1 and B2;  pp22 <= A2 and B2;  pp32 <= A3 and B2;
    pp03 <= A0 and B3;  pp13 <= A1 and B3;  pp23 <= A2 and B3;  pp33 <= A3 and B3;

    -- ── Row 1: add B0 row and B1 row ─────────────────────────────────────────
    -- bit 0: direct
    -- bit 1: HA(pp10, pp01)
    r1s1 <= pp10 xor pp01;
    r1c1 <= pp10 and pp01;
    -- bit 2: FA(pp20, pp11, r1c1)
    r1s2 <= pp20 xor pp11 xor r1c1;
    r1c2 <= (pp20 and pp11) or (pp20 and r1c1) or (pp11 and r1c1);
    -- bit 3: FA(pp30, pp21, r1c2)
    r1s3 <= pp30 xor pp21 xor r1c2;
    r1c3 <= (pp30 and pp21) or (pp30 and r1c2) or (pp21 and r1c2);
    -- bit 4: HA(pp31, r1c3)
    r1s4 <= pp31 xor r1c3;
    r1c4 <= pp31 and r1c3;

    -- ── Row 2: add B2 row to row-1 result ────────────────────────────────────
    -- bit 2: HA(r1s2, pp02)
    r2s2 <= r1s2 xor pp02;
    r2c2 <= r1s2 and pp02;
    -- bit 3: FA(r1s3, pp12, r2c2)
    r2s3 <= r1s3 xor pp12 xor r2c2;
    r2c3 <= (r1s3 and pp12) or (r1s3 and r2c2) or (pp12 and r2c2);
    -- bit 4: FA(r1s4, pp22, r2c3)
    r2s4 <= r1s4 xor pp22 xor r2c3;
    r2c4 <= (r1s4 and pp22) or (r1s4 and r2c3) or (pp22 and r2c3);
    -- bit 5: FA(r1c4, pp32, r2c4)
    r2s5 <= r1c4 xor pp32 xor r2c4;
    r2c5 <= (r1c4 and pp32) or (r1c4 and r2c4) or (pp32 and r2c4);

    -- ── Row 3: add B3 row to row-2 result ────────────────────────────────────
    -- bit 3: HA(r2s3, pp03)
    r3s3 <= r2s3 xor pp03;
    r3c3 <= r2s3 and pp03;
    -- bit 4: FA(r2s4, pp13, r3c3)
    r3s4 <= r2s4 xor pp13 xor r3c3;
    r3c4 <= (r2s4 and pp13) or (r2s4 and r3c3) or (pp13 and r3c3);
    -- bit 5: FA(r2s5, pp23, r3c4)
    r3s5 <= r2s5 xor pp23 xor r3c4;
    r3c5 <= (r2s5 and pp23) or (r2s5 and r3c4) or (pp23 and r3c4);
    -- bit 6: FA(r2c5, pp33, r3c5)
    r3s6 <= r2c5 xor pp33 xor r3c5;
    r3c6 <= (r2c5 and pp33) or (r2c5 and r3c5) or (pp33 and r3c5);

    -- ── Final product bits ────────────────────────────────────────────────────
    P0 <= pp00;
    P1 <= r1s1;
    P2 <= r2s2;
    P3 <= r3s3;
    P4 <= r3s4;
    P5 <= r3s5;
    P6 <= r3s6;
    P7 <= r3c6;
end Structural;
