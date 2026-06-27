#!/usr/bin/env bash
# Spot-test the 6 new ECE645 computer-arithmetic VHDL blocks.
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
       && ghdl -r --std=08 "${entity}_tb" --stop-time=50us 2>&1 | grep -q "PASS"; then
        echo "[PASS] $entity"; PASS=$((PASS+1))
    else
        echo "[FAIL] $entity"
        ghdl -r --std=08 "${entity}_tb" --stop-time=50us 2>&1 | tail -8
        FAIL=$((FAIL+1))
    fi
    rm -f "${entity}_tb" work-obj08.cf
}

# ── KS4 ───────────────────────────────────────────────────────────────────────
cat > ks4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity KS4_tb is end entity;
architecture sim of KS4_tb is
    component KS4
        port(A0,A1,A2,A3,B0,B1,B2,B3,CIN:in std_logic;
             S0,S1,S2,S3,COUT:out std_logic);
    end component;
    signal A,B : unsigned(3 downto 0) := (others=>'0');
    signal CIN,COUT : std_logic := '0';
    signal S : unsigned(3 downto 0);
begin
    uut: KS4 port map(A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),
                      CIN,S(0),S(1),S(2),S(3),COUT);
    process
        variable exp : unsigned(4 downto 0);
        variable ci  : integer;
    begin
        for ci in 0 to 1 loop
            if ci=0 then CIN<='0'; else CIN<='1'; end if;
            for ai in 0 to 15 loop
                for bi in 0 to 15 loop
                    A <= to_unsigned(ai,4); B <= to_unsigned(bi,4);
                    wait for 5 ns;
                    exp := ("0"&to_unsigned(ai,4)) + ("0"&to_unsigned(bi,4))
                           + to_unsigned(ci,5);
                    assert (COUT&S) = exp
                        report "FAIL KS4 A="&integer'image(ai)&
                               " B="&integer'image(bi)&
                               " CIN="&integer'image(ci) severity failure;
                end loop;
            end loop;
        end loop;
        report "KS4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test KS4 ks4.vhd ks4_tb.vhd

# ── BK4 ───────────────────────────────────────────────────────────────────────
cat > bk4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity BK4_tb is end entity;
architecture sim of BK4_tb is
    component BK4
        port(A0,A1,A2,A3,B0,B1,B2,B3,CIN:in std_logic;
             S0,S1,S2,S3,COUT:out std_logic);
    end component;
    signal A,B : unsigned(3 downto 0) := (others=>'0');
    signal CIN,COUT : std_logic := '0';
    signal S : unsigned(3 downto 0);
begin
    uut: BK4 port map(A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),
                      CIN,S(0),S(1),S(2),S(3),COUT);
    process
        variable exp : unsigned(4 downto 0);
    begin
        for ci in 0 to 1 loop
            if ci=0 then CIN<='0'; else CIN<='1'; end if;
            for ai in 0 to 15 loop
                for bi in 0 to 15 loop
                    A <= to_unsigned(ai,4); B <= to_unsigned(bi,4);
                    wait for 5 ns;
                    exp := ("0"&to_unsigned(ai,4)) + ("0"&to_unsigned(bi,4))
                           + to_unsigned(ci,5);
                    assert (COUT&S) = exp
                        report "FAIL BK4" severity failure;
                end loop;
            end loop;
        end loop;
        report "BK4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test BK4 bk4.vhd bk4_tb.vhd

# ── NONREST_DIV4 ──────────────────────────────────────────────────────────────
cat > nonrest_div4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity NONREST_DIV4_tb is end entity;
architecture sim of NONREST_DIV4_tb is
    component NONREST_DIV4
        port(N0,N1,N2,N3,D0,D1,D2,D3:in std_logic;
             Q0,Q1,Q2,Q3,R0,R1,R2,R3:out std_logic);
    end component;
    signal N,D : unsigned(3 downto 0) := (others=>'0');
    signal Q,R : unsigned(3 downto 0);
begin
    uut: NONREST_DIV4 port map(
        N(0),N(1),N(2),N(3),D(0),D(1),D(2),D(3),
        Q(0),Q(1),Q(2),Q(3),R(0),R(1),R(2),R(3));
    process
    begin
        for ni in 0 to 15 loop
            for di in 1 to 15 loop
                N <= to_unsigned(ni,4); D <= to_unsigned(di,4);
                wait for 10 ns;
                assert to_integer(Q) = ni/di and to_integer(R) = ni mod di
                    report "FAIL NONREST_DIV4 N="&integer'image(ni)&
                           " D="&integer'image(di)&
                           " Q="&integer'image(to_integer(Q))&
                           " R="&integer'image(to_integer(R)) severity failure;
            end loop;
        end loop;
        report "NONREST_DIV4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test NONREST_DIV4 nonrest_div4.vhd nonrest_div4_tb.vhd

# ── WALLACE3_4 ────────────────────────────────────────────────────────────────
cat > wallace3_4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity WALLACE3_4_tb is end entity;
architecture sim of WALLACE3_4_tb is
    component WALLACE3_4
        port(A0,A1,A2,A3,B0,B1,B2,B3,C0,C1,C2,C3:in std_logic;
             P0,P1,P2,P3,P4,P5:out std_logic);
    end component;
    signal A,B,C : unsigned(3 downto 0) := (others=>'0');
    signal P     : unsigned(5 downto 0);
begin
    uut: WALLACE3_4 port map(
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
                        report "FAIL WALLACE3_4" severity failure;
                end loop;
            end loop;
        end loop;
        report "WALLACE3_4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test WALLACE3_4 wallace3_4.vhd wallace3_4_tb.vhd

# ── MOD_ADD4 ──────────────────────────────────────────────────────────────────
cat > mod_add4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity MOD_ADD4_tb is end entity;
architecture sim of MOD_ADD4_tb is
    component MOD_ADD4
        port(A0,A1,A2,A3,B0,B1,B2,B3,M0,M1,M2,M3:in std_logic;
             R0,R1,R2,R3:out std_logic);
    end component;
    signal A,B,M : unsigned(3 downto 0) := (others=>'0');
    signal R     : unsigned(3 downto 0);
begin
    uut: MOD_ADD4 port map(
        A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),M(0),M(1),M(2),M(3),
        R(0),R(1),R(2),R(3));
    process
    begin
        -- Test with modulus 13 (prime, fits in 4 bits)
        M <= to_unsigned(13,4);
        for ai in 0 to 12 loop
            for bi in 0 to 12 loop
                A<=to_unsigned(ai,4); B<=to_unsigned(bi,4); wait for 10 ns;
                assert to_integer(R) = (ai+bi) mod 13
                    report "FAIL MOD_ADD4 mod13" severity failure;
            end loop;
        end loop;
        -- Test with modulus 7
        M <= to_unsigned(7,4);
        for ai in 0 to 6 loop
            for bi in 0 to 6 loop
                A<=to_unsigned(ai,4); B<=to_unsigned(bi,4); wait for 10 ns;
                assert to_integer(R) = (ai+bi) mod 7
                    report "FAIL MOD_ADD4 mod7" severity failure;
            end loop;
        end loop;
        report "MOD_ADD4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test MOD_ADD4 mod_add4.vhd mod_add4_tb.vhd

# ── SQ4 ───────────────────────────────────────────────────────────────────────
cat > sq4_tb.vhd << 'ENDVHD'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity SQ4_tb is end entity;
architecture sim of SQ4_tb is
    component SQ4
        port(A0,A1,A2,A3:in std_logic;
             P0,P1,P2,P3,P4,P5,P6,P7:out std_logic);
    end component;
    signal A : unsigned(3 downto 0) := (others=>'0');
    signal P : unsigned(7 downto 0);
begin
    uut: SQ4 port map(A(0),A(1),A(2),A(3),
                      P(0),P(1),P(2),P(3),P(4),P(5),P(6),P(7));
    process
    begin
        for ai in 0 to 15 loop
            A <= to_unsigned(ai,4); wait for 10 ns;
            assert to_integer(P) = ai*ai
                report "FAIL SQ4 A="&integer'image(ai)&
                       " P="&integer'image(to_integer(P)) severity failure;
        end loop;
        report "SQ4 PASS" severity note; wait;
    end process;
end architecture;
ENDVHD
try_test SQ4 sq4.vhd sq4_tb.vhd

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ]
