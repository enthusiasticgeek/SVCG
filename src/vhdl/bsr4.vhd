-- bsr4.vhd  (4-bit barrel shifter)
-- Shifts A by AMT positions (0-3).
-- MODE: "00" = logical left shift
--       "01" = logical right shift
--       "10" = arithmetic right shift (sign-extends A3)
-- Inputs:  A3..A0 (data), AMT1,AMT0 (shift amount), MODE1,MODE0 (direction/type)
-- Outputs: R3..R0 (result)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity BSR4 is
    Port ( A0    : in  STD_LOGIC;
           A1    : in  STD_LOGIC;
           A2    : in  STD_LOGIC;
           A3    : in  STD_LOGIC;
           AMT0  : in  STD_LOGIC;
           AMT1  : in  STD_LOGIC;
           MODE0 : in  STD_LOGIC;
           MODE1 : in  STD_LOGIC;
           R0    : out STD_LOGIC;
           R1    : out STD_LOGIC;
           R2    : out STD_LOGIC;
           R3    : out STD_LOGIC);
end BSR4;

architecture Behavioral of BSR4 is
begin
    process(A0,A1,A2,A3,AMT0,AMT1,MODE0,MODE1)
        variable A_v   : unsigned(3 downto 0);
        variable A_s   : signed(3 downto 0);
        variable amt   : integer range 0 to 3;
        variable mode  : std_logic_vector(1 downto 0);
        variable R_v   : unsigned(3 downto 0);
    begin
        A_v  := unsigned(std_logic_vector'(A3 & A2 & A1 & A0));
        A_s  := signed(std_logic_vector'(A3 & A2 & A1 & A0));
        amt  := to_integer(unsigned'(AMT1 & AMT0));
        mode := MODE1 & MODE0;

        case mode is
            when "00" =>   -- logical left
                R_v := shift_left(A_v, amt);
            when "01" =>   -- logical right
                R_v := shift_right(A_v, amt);
            when others => -- arithmetic right (10 or 11)
                R_v := unsigned(shift_right(A_s, amt));
        end case;

        R0 <= R_v(0);  R1 <= R_v(1);  R2 <= R_v(2);  R3 <= R_v(3);
    end process;
end Behavioral;
