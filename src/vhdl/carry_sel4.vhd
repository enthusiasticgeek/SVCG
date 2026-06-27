-- carry_sel4.vhd  (4-bit carry select adder)
-- Splits into two 2-bit halves.  The high half is computed twice
-- (assuming CIN=0 and CIN=1) and the correct result is muxed in when
-- the low-half carry is known.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity CARRY_SEL4 is
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
end CARRY_SEL4;

architecture Behavioral of CARRY_SEL4 is
    -- Low 2-bit ripple carry adder (bits 0-1)
    signal c1_lo, c2_lo : STD_LOGIC;
    signal s0_lo, s1_lo : STD_LOGIC;

    -- High 2-bit adder assuming carry-in = 0
    signal c3_h0, c4_h0   : STD_LOGIC;
    signal s2_h0, s3_h0   : STD_LOGIC;

    -- High 2-bit adder assuming carry-in = 1
    signal c3_h1, c4_h1   : STD_LOGIC;
    signal s2_h1, s3_h1   : STD_LOGIC;
begin
    -- ── Low half (bits 0-1) ──────────────────────────────────────────────────
    s0_lo  <= A0 xor B0 xor CIN;
    c1_lo  <= (A0 and B0) or (A0 and CIN) or (B0 and CIN);
    s1_lo  <= A1 xor B1 xor c1_lo;
    c2_lo  <= (A1 and B1) or (A1 and c1_lo) or (B1 and c1_lo);

    -- ── High half, assumed CIN=0 ─────────────────────────────────────────────
    s2_h0  <= A2 xor B2;
    c3_h0  <= A2 and B2;
    s3_h0  <= A3 xor B3 xor c3_h0;
    c4_h0  <= (A3 and B3) or (A3 and c3_h0) or (B3 and c3_h0);

    -- ── High half, assumed CIN=1 ─────────────────────────────────────────────
    s2_h1  <= A2 xor B2 xor '1';
    c3_h1  <= (A2 and B2) or (A2 and '1') or (B2 and '1');
    s3_h1  <= A3 xor B3 xor c3_h1;
    c4_h1  <= (A3 and B3) or (A3 and c3_h1) or (B3 and c3_h1);

    -- ── Mux: select high-half result based on low-half carry ─────────────────
    S0   <= s0_lo;
    S1   <= s1_lo;
    S2   <= s2_h0 when c2_lo = '0' else s2_h1;
    S3   <= s3_h0 when c2_lo = '0' else s3_h1;
    COUT <= c4_h0 when c2_lo = '0' else c4_h1;
end Behavioral;
