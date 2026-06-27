-- booth4_mult4.vhd  (4-bit signed radix-4 Modified Booth multiplier)
-- Encodes multiplier B in overlapping groups of 3 bits (radix-4 MBE).
-- For a 4-bit multiplier two partial products suffice (vs four for radix-2).
-- Each partial product PP = {0, ±A, ±2A} selected by the Booth digit.
-- Result: 8-bit signed product P = A * B.
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity BOOTH4_MULT4 is
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
end BOOTH4_MULT4;

architecture Behavioral of BOOTH4_MULT4 is
begin
    process(A0, A1, A2, A3, B0, B1, B2, B3)
        variable A_v  : signed(5 downto 0);   -- sign-extended to 6 bits (avoids ±2A overflow)
        variable B_v  : signed(3 downto 0);
        variable acc  : signed(8 downto 0);   -- 9-bit accumulator
        -- Radix-4 Booth encoding triplet: (b_{2i+1}, b_{2i}, b_{2i-1})
        variable tri  : std_logic_vector(2 downto 0);
        variable pp   : signed(5 downto 0);   -- partial product (±A or ±2A), 6-bit
    begin
        A_v := signed(std_logic_vector'(A3 & A3 & A3 & A2 & A1 & A0)); -- sign-extend A to 6-bit
        B_v := signed(std_logic_vector'(B3 & B2 & B1 & B0));
        acc := (others => '0');

        -- Group 0: bits (B1, B0, 0)  — implicit b_{-1} = 0
        tri := std_logic_vector(B_v(1 downto 0)) & '0';
        case tri is
            when "001" | "010" => pp :=  A_v;
            when "011"         => pp :=  shift_left(A_v, 1);
            when "100"         => pp := -shift_left(A_v, 1);
            when "101" | "110" => pp := -A_v;
            when others        => pp := (others => '0');  -- "000" or "111"
        end case;
        acc := acc + resize(pp, 9);

        -- Group 1: bits (B3, B2, B1) — this is the MSB group
        tri := std_logic_vector(B_v(3 downto 1));
        case tri is
            when "001" | "010" => pp :=  A_v;
            when "011"         => pp :=  shift_left(A_v, 1);
            when "100"         => pp := -shift_left(A_v, 1);
            when "101" | "110" => pp := -A_v;
            when others        => pp := (others => '0');
        end case;
        -- Group 1 partial product is at weight 2^2
        acc := acc + shift_left(resize(pp, 9), 2);

        P0 <= acc(0);  P1 <= acc(1);  P2 <= acc(2);  P3 <= acc(3);
        P4 <= acc(4);  P5 <= acc(5);  P6 <= acc(6);  P7 <= acc(7);
    end process;
end Behavioral;
