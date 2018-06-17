clc
clear
close all

flowout=[];
levels=[];
pid=[];
flowin=[];

for i=1:239
    load(['simout',num2str(i),'.mat']);
    
    flowout=[flowout;simout.signal2.data];    
    levels=[levels;simout.signal1.signal2.data];
    pid=[pid;simout.signal1.signal1.signal1.data];
    flowin=[flowin;simout.signal1.signal1.signal2.data];
        
end


plot(levels(:,2))