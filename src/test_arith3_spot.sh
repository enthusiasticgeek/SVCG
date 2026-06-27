#!/usr/bin/env bash
# Spot-test the 7 ECE645 batch-3 computer-arithmetic VHDL blocks.
# Run from MSYS2 MinGW64 shell inside SVCG/src/.
set -e
PASS=0; FAIL=0

VHDLDIR="/c/Users/upaas/SVCG/src/vhdl"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT
cd "$TMPDIR"

try_test() {
    local entity="$1"; local vhd="$2"; local tbfile="$3"
    if ghdl -a --std=08 "$VHDLDIR/$vhd" "$tbfile" \
       && ghdl -e --std=08 "${entity}_tb" \
       && ghdl -r --std=08 "${entity}_tb" --stop-time=200us 2>&1 | grep -q "PASS"; then
        echo "[PASS] $entity"; PASS=$((PASS+1))
    else
        echo "[FAIL] $entity"
        ghdl -r --std=08 "${entity}_tb" --stop-time=200us 2>&1 | tail -10
        FAIL=$((FAIL+1))
    fi
    rm -f "${entity}_tb" work-obj08.cf
}

# ── GF_ADD4 ───────────────────────────────────────────────────────────────────
cat > gf_add4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity GF_ADD4_tb is end entity;
architecture sim of GF_ADD4_tb is
    component GF_ADD4
        port(A0,A1,A2,A3,B0,B1,B2,B3:in std_logic; R0,R1,R2,R3:out std_logic);
    end component;
    signal A,B : unsigned(3 downto 0) := (others=>'0');
    signal R   : unsigned(3 downto 0);
begin
    uut: GF_ADD4 port map(A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),
                           R(0),R(1),R(2),R(3));
    process
    begin
        for ai in 0 to 15 loop
            for bi in 0 to 15 loop
                A <= to_unsigned(ai,4); B <= to_unsigned(bi,4);
                wait for 5 ns;
                assert R = (to_unsigned(ai,4) xor to_unsigned(bi,4))
                    report "FAIL GF_ADD4" severity failure;
            end loop;
        end loop;
        report "GF_ADD4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test GF_ADD4 gf_add4.vhd gf_add4_tb.vhd

# ── GF_MUL4 ───────────────────────────────────────────────────────────────────
cat > gf_mul4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity GF_MUL4_tb is end entity;
architecture sim of GF_MUL4_tb is
    component GF_MUL4
        port(A0,A1,A2,A3,B0,B1,B2,B3:in std_logic; R0,R1,R2,R3:out std_logic);
    end component;
    signal A,B,R : unsigned(3 downto 0);
    -- Reference: multiply in GF(2^4) mod x^4+x+1
    function gf_mul(a_in, b_in : unsigned(3 downto 0)) return unsigned is
        variable a_v, b_v, p_v : unsigned(3 downto 0);
        variable carry : std_logic;
    begin
        a_v := a_in; b_v := b_in; p_v := (others=>'0');
        for i in 0 to 3 loop
            if b_v(0) = '1' then p_v := p_v xor a_v; end if;
            carry := a_v(3);
            a_v := a_v(2 downto 0) & '0';
            if carry = '1' then a_v := a_v xor "0011"; end if;  -- mod x^4+x+1 = 0x3 low bits
            b_v := '0' & b_v(3 downto 1);
        end loop;
        return p_v;
    end function;
begin
    uut: GF_MUL4 port map(A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),
                           R(0),R(1),R(2),R(3));
    process
        variable exp : unsigned(3 downto 0);
    begin
        for ai in 0 to 15 loop
            for bi in 0 to 15 loop
                A <= to_unsigned(ai,4); B <= to_unsigned(bi,4);
                wait for 10 ns;
                exp := gf_mul(to_unsigned(ai,4), to_unsigned(bi,4));
                assert R = exp
                    report "FAIL GF_MUL4 A="&integer'image(ai)&
                           " B="&integer'image(bi)&
                           " got="&integer'image(to_integer(R))&
                           " exp="&integer'image(to_integer(exp)) severity failure;
            end loop;
        end loop;
        report "GF_MUL4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test GF_MUL4 gf_mul4.vhd gf_mul4_tb.vhd

# ── BOOTH4_MULT4 ──────────────────────────────────────────────────────────────
cat > booth4_mult4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity BOOTH4_MULT4_tb is end entity;
architecture sim of BOOTH4_MULT4_tb is
    component BOOTH4_MULT4
        port(A0,A1,A2,A3,B0,B1,B2,B3:in std_logic;
             P0,P1,P2,P3,P4,P5,P6,P7:out std_logic);
    end component;
    signal A,B : signed(3 downto 0) := (others=>'0');
    signal P   : signed(7 downto 0);
begin
    uut: BOOTH4_MULT4 port map(
        A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),
        P(0),P(1),P(2),P(3),P(4),P(5),P(6),P(7));
    process
    begin
        for ai in -8 to 7 loop
            for bi in -8 to 7 loop
                A <= to_signed(ai,4); B <= to_signed(bi,4);
                wait for 10 ns;
                assert to_integer(P) = ai*bi
                    report "FAIL BOOTH4_MULT4 A="&integer'image(ai)&
                           " B="&integer'image(bi)&
                           " P="&integer'image(to_integer(P)) severity failure;
            end loop;
        end loop;
        report "BOOTH4_MULT4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test BOOTH4_MULT4 booth4_mult4.vhd booth4_mult4_tb.vhd

# ── DADDA4 ────────────────────────────────────────────────────────────────────
cat > dadda4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity DADDA4_tb is end entity;
architecture sim of DADDA4_tb is
    component DADDA4
        port(A0,A1,A2,A3,B0,B1,B2,B3,C0,C1,C2,C3:in std_logic;
             P0,P1,P2,P3,P4,P5:out std_logic);
    end component;
    signal A,B,C : unsigned(3 downto 0) := (others=>'0');
    signal P     : unsigned(5 downto 0);
begin
    uut: DADDA4 port map(
        A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),C(0),C(1),C(2),C(3),
        P(0),P(1),P(2),P(3),P(4),P(5));
    process
    begin
        for ai in 0 to 15 loop
            for bi in 0 to 15 loop
                for ci in 0 to 15 loop
                    A<=to_unsigned(ai,4); B<=to_unsigned(bi,4);
                    C<=to_unsigned(ci,4); wait for 5 ns;
                    assert to_integer(P) = ai+bi+ci
                        report "FAIL DADDA4" severity failure;
                end loop;
            end loop;
        end loop;
        report "DADDA4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test DADDA4 dadda4.vhd dadda4_tb.vhd

# ── SRT_DIV4 ──────────────────────────────────────────────────────────────────
cat > srt_div4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity SRT_DIV4_tb is end entity;
architecture sim of SRT_DIV4_tb is
    component SRT_DIV4
        port(N0,N1,N2,N3,D0,D1,D2,D3:in std_logic;
             Q0,Q1,Q2,Q3,R0,R1,R2,R3:out std_logic);
    end component;
    signal N,D : unsigned(3 downto 0) := (others=>'0');
    signal Q,R : unsigned(3 downto 0);
begin
    uut: SRT_DIV4 port map(
        N(0),N(1),N(2),N(3),D(0),D(1),D(2),D(3),
        Q(0),Q(1),Q(2),Q(3),R(0),R(1),R(2),R(3));
    process
    begin
        for ni in 0 to 15 loop
            for di in 1 to 15 loop
                N <= to_unsigned(ni,4); D <= to_unsigned(di,4);
                wait for 10 ns;
                assert to_integer(Q) = ni/di and to_integer(R) = ni mod di
                    report "FAIL SRT_DIV4 N="&integer'image(ni)&
                           " D="&integer'image(di)&
                           " Q="&integer'image(to_integer(Q))&
                           " R="&integer'image(to_integer(R)) severity failure;
            end loop;
        end loop;
        report "SRT_DIV4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test SRT_DIV4 srt_div4.vhd srt_div4_tb.vhd

# ── BSR4 ──────────────────────────────────────────────────────────────────────
cat > bsr4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity BSR4_tb is end entity;
architecture sim of BSR4_tb is
    component BSR4
        port(A0,A1,A2,A3,AMT0,AMT1,MODE0,MODE1:in std_logic;
             R0,R1,R2,R3:out std_logic);
    end component;
    signal A           : unsigned(3 downto 0) := (others=>'0');
    signal AMT         : unsigned(1 downto 0) := (others=>'0');
    signal MODE        : std_logic_vector(1 downto 0) := (others=>'0');
    signal R           : unsigned(3 downto 0);
begin
    uut: BSR4 port map(A(0),A(1),A(2),A(3),AMT(0),AMT(1),MODE(0),MODE(1),
                       R(0),R(1),R(2),R(3));
    process
        variable exp : unsigned(3 downto 0);
        variable As  : signed(3 downto 0);
    begin
        -- logical left
        MODE <= "00";
        for ai in 0 to 15 loop
            for sh in 0 to 3 loop
                A <= to_unsigned(ai,4); AMT <= to_unsigned(sh,2); wait for 5 ns;
                exp := shift_left(to_unsigned(ai,4), sh);
                assert R = exp report "FAIL BSR4 SHL" severity failure;
            end loop;
        end loop;
        -- logical right
        MODE <= "01";
        for ai in 0 to 15 loop
            for sh in 0 to 3 loop
                A <= to_unsigned(ai,4); AMT <= to_unsigned(sh,2); wait for 5 ns;
                exp := shift_right(to_unsigned(ai,4), sh);
                assert R = exp report "FAIL BSR4 SHR" severity failure;
            end loop;
        end loop;
        -- arithmetic right
        MODE <= "10";
        for ai in 0 to 15 loop
            for sh in 0 to 3 loop
                A <= to_unsigned(ai,4); AMT <= to_unsigned(sh,2); wait for 5 ns;
                As  := signed(to_unsigned(ai,4));
                exp := unsigned(shift_right(As, sh));
                assert R = exp report "FAIL BSR4 SAR" severity failure;
            end loop;
        end loop;
        report "BSR4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test BSR4 bsr4.vhd bsr4_tb.vhd

# ── MOD_MUL4 ──────────────────────────────────────────────────────────────────
cat > mod_mul4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity MOD_MUL4_tb is end entity;
architecture sim of MOD_MUL4_tb is
    component MOD_MUL4
        port(A0,A1,A2,A3,B0,B1,B2,B3,M0,M1,M2,M3:in std_logic;
             R0,R1,R2,R3:out std_logic);
    end component;
    signal A,B,M : unsigned(3 downto 0) := (others=>'0');
    signal R      : unsigned(3 downto 0);
begin
    uut: MOD_MUL4 port map(
        A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),M(0),M(1),M(2),M(3),
        R(0),R(1),R(2),R(3));
    process
    begin
        -- modulus 13
        M <= to_unsigned(13,4);
        for ai in 0 to 12 loop
            for bi in 0 to 12 loop
                A<=to_unsigned(ai,4); B<=to_unsigned(bi,4); wait for 10 ns;
                assert to_integer(R) = (ai*bi) mod 13
                    report "FAIL MOD_MUL4 mod13" severity failure;
            end loop;
        end loop;
        -- modulus 7
        M <= to_unsigned(7,4);
        for ai in 0 to 6 loop
            for bi in 0 to 6 loop
                A<=to_unsigned(ai,4); B<=to_unsigned(bi,4); wait for 10 ns;
                assert to_integer(R) = (ai*bi) mod 7
                    report "FAIL MOD_MUL4 mod7" severity failure;
            end loop;
        end loop;
        report "MOD_MUL4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test MOD_MUL4 mod_mul4.vhd mod_mul4_tb.vhd

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ]
