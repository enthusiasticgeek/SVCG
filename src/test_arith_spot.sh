#!/usr/bin/env bash
# Spot-test all 6 new computer-arithmetic VHDL blocks under GHDL.
# Run from: MSYS2 MinGW64 shell inside SVCG/src/
# Usage: bash test_arith_spot.sh

set -e
PASS=0; FAIL=0

run_ghdl() {
    local entity="$1"; local vhd="$2"; local tb_vhd="$3"
    echo "=== $entity ==="
    ghdl -a --std=08 "../vhdl/$vhd" "$tb_vhd" 2>&1
    ghdl -e --std=08 "${entity}_tb" 2>&1
    ghdl -r --std=08 "${entity}_tb" --stop-time=500ns 2>&1
    echo "OK"
}

TMPDIR="$(mktemp -d)"
trap "rm -rf $TMPDIR" EXIT
cd "$TMPDIR"

# ── CLA4 ──────────────────────────────────────────────────────────────────────
cat > cla4_tb.vhd <<'EOF'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity CLA4_tb is end;
architecture sim of CLA4_tb is
    component CLA4 port(A0,A1,A2,A3,B0,B1,B2,B3,CIN:in std_logic;
                        S0,S1,S2,S3,COUT:out std_logic); end component;
    signal A,B: unsigned(3 downto 0):=(others=>'0');
    signal CIN: std_logic:='0';
    signal S: unsigned(3 downto 0); signal CO: std_logic;
begin
    uut: CLA4 port map(A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),CIN,
                       S(0),S(1),S(2),S(3),CO);
    process
        variable expected: unsigned(4 downto 0);
    begin
        for ai in 0 to 15 loop for bi in 0 to 15 loop
            A <= to_unsigned(ai,4); B <= to_unsigned(bi,4); CIN<='0';
            wait for 10 ns;
            expected := ('0'&to_unsigned(ai,4)) + ('0'&to_unsigned(bi,4));
            assert (CO&S) = expected
                report "FAIL CLA4 A=" & integer'image(ai) &
                       " B=" & integer'image(bi) severity failure;
        end loop; end loop;
        report "CLA4 exhaustive PASS" severity note; wait;
    end process;
end;
EOF
if ghdl -a --std=08 /c/Users/upaas/SVCG/src/vhdl/cla4.vhd cla4_tb.vhd \
   && ghdl -e --std=08 CLA4_tb \
   && ghdl -r --std=08 CLA4_tb --stop-time=5us 2>&1 | grep -q "PASS"; then
    echo "[PASS] CLA4"; PASS=$((PASS+1))
else
    echo "[FAIL] CLA4"; FAIL=$((FAIL+1))
fi

# ── CARRY_SEL4 ────────────────────────────────────────────────────────────────
cat > carry_sel4_tb.vhd <<'EOF'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity CARRY_SEL4_tb is end;
architecture sim of CARRY_SEL4_tb is
    component CARRY_SEL4 port(A0,A1,A2,A3,B0,B1,B2,B3,CIN:in std_logic;
                              S0,S1,S2,S3,COUT:out std_logic); end component;
    signal A,B: unsigned(3 downto 0):=(others=>'0');
    signal CIN: std_logic:='0';
    signal S: unsigned(3 downto 0); signal CO: std_logic;
begin
    uut: CARRY_SEL4 port map(A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),CIN,
                             S(0),S(1),S(2),S(3),CO);
    process
        variable expected: unsigned(4 downto 0);
    begin
        for ai in 0 to 15 loop for bi in 0 to 15 loop
            A<=to_unsigned(ai,4); B<=to_unsigned(bi,4); CIN<='0'; wait for 10 ns;
            expected:=('0'&to_unsigned(ai,4))+('0'&to_unsigned(bi,4));
            assert (CO&S)=expected
                report "FAIL CARRY_SEL4" severity failure;
        end loop; end loop;
        report "CARRY_SEL4 exhaustive PASS" severity note; wait;
    end process;
end;
EOF
if ghdl -a --std=08 /c/Users/upaas/SVCG/src/vhdl/carry_sel4.vhd carry_sel4_tb.vhd \
   && ghdl -e --std=08 CARRY_SEL4_tb \
   && ghdl -r --std=08 CARRY_SEL4_tb --stop-time=5us 2>&1 | grep -q "PASS"; then
    echo "[PASS] CARRY_SEL4"; PASS=$((PASS+1))
else
    echo "[FAIL] CARRY_SEL4"; FAIL=$((FAIL+1))
fi

# ── CSA ───────────────────────────────────────────────────────────────────────
cat > csa_tb.vhd <<'EOF'
library IEEE; use IEEE.STD_LOGIC_1164.ALL;
entity CSA_tb is end;
architecture sim of CSA_tb is
    component CSA port(A,B,C:in std_logic; SO,CO:out std_logic); end component;
    signal A,B,C,SO,CO: std_logic;
begin
    uut: CSA port map(A,B,C,SO,CO);
    process
        variable s: integer;
    begin
        for combo in 0 to 7 loop
            A<=std_logic'val(combo/4+2); B<=std_logic'val((combo/2) mod 2+2);
            C<=std_logic'val(combo mod 2+2); wait for 10 ns;
            s:=(to_integer(unsigned'(""&A))+to_integer(unsigned'(""&B))+to_integer(unsigned'(""&C)));
            assert to_integer(unsigned'(""&CO))*2+to_integer(unsigned'(""&SO))=s
                report "FAIL CSA" severity failure;
        end loop;
        report "CSA truth table PASS" severity note; wait;
    end process;
end;
EOF
# CSA tb uses tricky std_logic arithmetic; use simpler direct check instead
cat > csa_tb.vhd <<'EOF'
library IEEE; use IEEE.STD_LOGIC_1164.ALL;
entity CSA_tb is end;
architecture sim of CSA_tb is
    component CSA port(A,B,C:in std_logic; SO,CO:out std_logic); end component;
    signal A,B,C,SO,CO: std_logic;
begin
    uut: CSA port map(A,B,C,SO,CO);
    process
    begin
        -- truth table: A B C -> CO SO (binary sum)
        A<='0';B<='0';C<='0'; wait for 10 ns; assert SO='0' and CO='0' report "000" severity failure;
        A<='0';B<='0';C<='1'; wait for 10 ns; assert SO='1' and CO='0' report "001" severity failure;
        A<='0';B<='1';C<='0'; wait for 10 ns; assert SO='1' and CO='0' report "010" severity failure;
        A<='0';B<='1';C<='1'; wait for 10 ns; assert SO='0' and CO='1' report "011" severity failure;
        A<='1';B<='0';C<='0'; wait for 10 ns; assert SO='1' and CO='0' report "100" severity failure;
        A<='1';B<='0';C<='1'; wait for 10 ns; assert SO='0' and CO='1' report "101" severity failure;
        A<='1';B<='1';C<='0'; wait for 10 ns; assert SO='0' and CO='1' report "110" severity failure;
        A<='1';B<='1';C<='1'; wait for 10 ns; assert SO='1' and CO='1' report "111" severity failure;
        report "CSA truth table PASS" severity note; wait;
    end process;
end;
EOF
if ghdl -a --std=08 /c/Users/upaas/SVCG/src/vhdl/csa.vhd csa_tb.vhd \
   && ghdl -e --std=08 CSA_tb \
   && ghdl -r --std=08 CSA_tb --stop-time=200ns 2>&1 | grep -q "PASS"; then
    echo "[PASS] CSA"; PASS=$((PASS+1))
else
    echo "[FAIL] CSA"; FAIL=$((FAIL+1))
fi

# ── ARRAY_MULT4 ───────────────────────────────────────────────────────────────
cat > array_mult4_tb.vhd <<'EOF'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity ARRAY_MULT4_tb is end;
architecture sim of ARRAY_MULT4_tb is
    component ARRAY_MULT4 port(A0,A1,A2,A3,B0,B1,B2,B3:in std_logic;
                               P0,P1,P2,P3,P4,P5,P6,P7:out std_logic); end component;
    signal A,B: unsigned(3 downto 0):=(others=>'0');
    signal P: unsigned(7 downto 0);
begin
    uut: ARRAY_MULT4 port map(A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),
                              P(0),P(1),P(2),P(3),P(4),P(5),P(6),P(7));
    process
    begin
        for ai in 0 to 15 loop for bi in 0 to 15 loop
            A<=to_unsigned(ai,4); B<=to_unsigned(bi,4); wait for 10 ns;
            assert P=to_unsigned(ai*bi,8)
                report "FAIL ARRAY_MULT4 A="&integer'image(ai)&" B="&integer'image(bi) severity failure;
        end loop; end loop;
        report "ARRAY_MULT4 exhaustive PASS" severity note; wait;
    end process;
end;
EOF
if ghdl -a --std=08 /c/Users/upaas/SVCG/src/vhdl/array_mult4.vhd array_mult4_tb.vhd \
   && ghdl -e --std=08 ARRAY_MULT4_tb \
   && ghdl -r --std=08 ARRAY_MULT4_tb --stop-time=50us 2>&1 | grep -q "PASS"; then
    echo "[PASS] ARRAY_MULT4"; PASS=$((PASS+1))
else
    echo "[FAIL] ARRAY_MULT4"; FAIL=$((FAIL+1))
fi

# ── BOOTH_MULT4 ───────────────────────────────────────────────────────────────
cat > booth_mult4_tb.vhd <<'EOF'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity BOOTH_MULT4_tb is end;
architecture sim of BOOTH_MULT4_tb is
    component BOOTH_MULT4 port(A0,A1,A2,A3,B0,B1,B2,B3:in std_logic;
                               P0,P1,P2,P3,P4,P5,P6,P7:out std_logic); end component;
    signal A,B: signed(3 downto 0):=(others=>'0');
    signal P: signed(7 downto 0);
begin
    uut: BOOTH_MULT4 port map(A(0),A(1),A(2),A(3),B(0),B(1),B(2),B(3),
                              P(0),P(1),P(2),P(3),P(4),P(5),P(6),P(7));
    process
    begin
        for ai in -8 to 7 loop for bi in -8 to 7 loop
            A<=to_signed(ai,4); B<=to_signed(bi,4); wait for 10 ns;
            assert P=to_signed(ai*bi,8)
                report "FAIL BOOTH_MULT4 A="&integer'image(ai)&" B="&integer'image(bi) severity failure;
        end loop; end loop;
        report "BOOTH_MULT4 exhaustive PASS" severity note; wait;
    end process;
end;
EOF
if ghdl -a --std=08 /c/Users/upaas/SVCG/src/vhdl/booth_mult4.vhd booth_mult4_tb.vhd \
   && ghdl -e --std=08 BOOTH_MULT4_tb \
   && ghdl -r --std=08 BOOTH_MULT4_tb --stop-time=50us 2>&1 | grep -q "PASS"; then
    echo "[PASS] BOOTH_MULT4"; PASS=$((PASS+1))
else
    echo "[FAIL] BOOTH_MULT4"; FAIL=$((FAIL+1))
fi

# ── REST_DIV4 ─────────────────────────────────────────────────────────────────
cat > rest_div4_tb.vhd <<'EOF'
library IEEE; use IEEE.STD_LOGIC_1164.ALL; use IEEE.NUMERIC_STD.ALL;
entity REST_DIV4_tb is end;
architecture sim of REST_DIV4_tb is
    component REST_DIV4 port(N0,N1,N2,N3,D0,D1,D2,D3:in std_logic;
                             Q0,Q1,Q2,Q3,R0,R1,R2,R3:out std_logic); end component;
    signal N,D: unsigned(3 downto 0):=(others=>'0');
    signal Q,R: unsigned(3 downto 0);
begin
    uut: REST_DIV4 port map(N(0),N(1),N(2),N(3),D(0),D(1),D(2),D(3),
                            Q(0),Q(1),Q(2),Q(3),R(0),R(1),R(2),R(3));
    process
    begin
        for ni in 0 to 15 loop
            for di in 1 to 15 loop  -- skip divisor=0
                N<=to_unsigned(ni,4); D<=to_unsigned(di,4); wait for 10 ns;
                assert to_integer(Q)=ni/di and to_integer(R)=ni mod di
                    report "FAIL REST_DIV4 N="&integer'image(ni)&" D="&integer'image(di)
                           &" Q="&integer'image(to_integer(Q))&" R="&integer'image(to_integer(R))
                    severity failure;
            end loop;
        end loop;
        report "REST_DIV4 exhaustive PASS" severity note; wait;
    end process;
end;
EOF
if ghdl -a --std=08 /c/Users/upaas/SVCG/src/vhdl/rest_div4.vhd rest_div4_tb.vhd \
   && ghdl -e --std=08 REST_DIV4_tb \
   && ghdl -r --std=08 REST_DIV4_tb --stop-time=50us 2>&1 | grep -q "PASS"; then
    echo "[PASS] REST_DIV4"; PASS=$((PASS+1))
else
    echo "[FAIL] REST_DIV4"; FAIL=$((FAIL+1))
fi

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ]
