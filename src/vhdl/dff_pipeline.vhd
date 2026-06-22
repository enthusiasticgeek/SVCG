-- dff_pipeline.vhd  D Flip-Flop with synchronous active-low reset (pipeline stage)
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity DFF_PIPELINE is
    Port ( D     : in  STD_LOGIC;
           CLK   : in  STD_LOGIC;
           N_RST : in  STD_LOGIC;  -- Active-low synchronous reset
           Q     : out STD_LOGIC
         );
end DFF_PIPELINE;

architecture Behavioral of DFF_PIPELINE is
begin
    process(CLK)
    begin
        if rising_edge(CLK) then
            if N_RST = '0' then
                Q <= '0';
            else
                Q <= D;
            end if;
        end if;
    end process;
end Behavioral;
