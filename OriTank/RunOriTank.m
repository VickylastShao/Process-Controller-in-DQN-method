clc
close all
clear

load('initialparas.mat');
load('tank.mat');

I=0;

buttomarea=1;
heightoftank=2;
maxinflow=0.5;
outpipcrosssection=0.05;
Timedelay=0;

while(buttomarea>0&&buttomarea<100)
    
    I = I + 1;
    
    % 特性发生变化
    turningpoint=1;
    
    if I>turningpoint
        buttomarea=1;
        heightoftank=2;
        maxinflow=0.5;
        outpipcrosssection=0.05;
        Timedelay=0+(I-turningpoint)*0.02;
    end
    
    sim('sltank');
    
    save(['simout',num2str(I)], 'simout')
    
    disp(' ');
    disp(['第',num2str(I),'轮 结束！']);
    
end
