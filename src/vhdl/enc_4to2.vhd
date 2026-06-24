-- enc_4to2.vhd  (4-to-2 priority encoder, I3 highest priority)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ENC_4TO2 is
    Port ( I0    : in  STD_LOGIC;
           I1    : in  STD_LOGIC;
           I2    : in  STD_LOGIC;
           I3    : in  STD_LOGIC;
           Y0    : out STD_LOGIC;
           Y1    : out STD_LOGIC;
           VALID : out STD_LOGIC);
end ENC_4TO2;

architecture Behavioral of ENC_4TO2 is
begin
    process(I0, I1, I2, I3)
    begin
        if I3 = '1' then
            Y1 <= '1'; Y0 <= '1'; VALID <= '1';
        elsif I2 = '1' then
            Y1 <= '1'; Y0 <= '0'; VALID <= '1';
        elsif I1 = '1' then
            Y1 <= '0'; Y0 <= '1'; VALID <= '1';
        elsif I0 = '1' then
            Y1 <= '0'; Y0 <= '0'; VALID <= '1';
        else
            Y1 <= '0'; Y0 <= '0'; VALID <= '0';
        end if;
    end process;
end Behavioral;
