clc
close all
clear

%%


[jsonModel,jsonWeight]=GetPolicyModel();

levelSet=linspace(0.5,1.5,100);
level=linspace(0.5,1.5,100);
massflow=0.3;

nx1=length(levelSet);
nx2=length(level);

[levelSetMesh,levelMesh]=meshgrid(levelSet,level);

states=ones(nx1*nx2,3);

for i=1:nx1
    for j=1:nx2
        states((i-1)*nx2+j,1)=levelSetMesh(j,i);
        states((i-1)*nx2+j,2)=levelMesh(j,i);
    end
end
states(:,3)=massflow;




BestPolicy=NNPolicyFun(states,jsonModel,jsonWeight);



X1=states(:,1);
X2=states(:,2);
Y=BestPolicy;

% figure
% plot3(X1,X2,Y,'ro');
% xlabel('水位')
% ylabel('入口流量')


[X1,X2,Y]=griddata(X1,X2,Y,linspace(min(X1),max(X1),nx1)',linspace(min(X2),max(X2),nx2),'linear');

figure
surf(X1,X2,Y)
xlabel('水位设定值')
ylabel('当前水位')
zlabel('最佳动作')
title(['入口流量： ',num2str(massflow)]);




%%
for level=0.95:0.025:1.05
[jsonModel,jsonWeight]=GetQModel();

levelSet=1;
% level=0.98;

massflow=linspace(0,0.5,100);
action=linspace(-1,1,100);

nx1=length(massflow);
nx2=length(action);

[massflowMesh,actionMesh]=meshgrid(massflow,action);

statesaction=ones(nx1*nx2,4);

statesaction(:,1)=levelSet;
statesaction(:,2)=level;

for i=1:nx1
    for j=1:nx2
        statesaction((i-1)*nx2+j,3)=massflowMesh(j,i);
        statesaction((i-1)*nx2+j,4)=actionMesh(j,i);
    end
end


Qvalue=NNQFun(statesaction,jsonModel,jsonWeight);



X1=statesaction(:,3);
X2=statesaction(:,4);
Y=Qvalue;

% figure
% plot3(X1,X2,Y,'ro');
% xlabel('水位')
% ylabel('入口流量')


[X1,X2,Y]=griddata(X1,X2,Y,linspace(min(X1),max(X1),nx1)',linspace(min(X2),max(X2),nx2),'linear');

figure
surf(X1,X2,Y)
xlabel('入口流量')
ylabel('动作')
zlabel('Q值')
title(['水位设定值:',num2str(levelSet),'当前水位:',num2str(level)]);

end

%%


function [jsonModel,jsonWeight]=GetPolicyModel()
while(true)
    try
        addpath(genpath([pwd,'\jsonlab-1.5']));        
        jsonModel=loadjson('PolicyModel.json');        
        jsonWeight=loadjson('PolicyWeight.json');        
        break;
    catch
        disp(' ');
        disp(' try to reload PolicyModel');
    end
end
end

function Policy=NNPolicyFun(input,jsonModel,jsonWeight)

MedValue=input;
config=jsonModel.config;
j=1;
for i=1:length(config)
    switch config{i}.class_name
        case 'Dense'
            MedValue=MedValue*jsonWeight{j}+jsonWeight{j+1};
            j=j+2;
        case 'Activation'
            config_i=config{i}.config;
            switch config_i.activation
                case 'relu'
                    MedValue=max(0,MedValue);
                case 'sigmoid'
                    MedValue=sigmf(MedValue,[1 0]);
                case 'tanh'
                    MedValue=tanh(MedValue);
                case 'selu'
                    alpha = 1.6732632423543772848170429916717;
                    scale = 1.0507009873554804934193349852946;
                    [r,c]=size(MedValue);
                    for m=1:r
                        for n=1:c
                            if(MedValue(m,n)>0)
                                MedValue(m,n)=scale*MedValue(m,n);
                            else
                                MedValue(m,n)=scale*(alpha*(exp(MedValue(m,n))-1));
                            end
                        end
                    end
            end
    end
end
%policymodel的输出层激活函数为sigmoid 输出在0~1之间 对应的实际动作是-0.5~0.5之间
Policy=MedValue-0.5;
end


function [jsonModel,jsonWeight]=GetQModel()
while(true)
    try
        addpath(genpath([pwd,'\jsonlab-1.5']));        
        jsonModel=loadjson('QModel.json');        
        jsonWeight=loadjson('QWeight.json');        
        break;
    catch
        disp(' ');
        disp(' try to reload QModel');
    end
end
end

function Q=NNQFun(input,jsonModel,jsonWeight)
MedValue=input;
config=jsonModel.config;
j=1;
for i=1:length(config)
    switch config{i}.class_name
        case 'Dense'
            MedValue=MedValue*jsonWeight{j}+jsonWeight{j+1};
            j=j+2;
        case 'Activation'
            config_i=config{i}.config;
            switch config_i.activation
                case 'relu'
                    MedValue=max(0,MedValue);
                case 'sigmoid'
                    MedValue=sigmf(MedValue,[1 0]);
                case 'tanh'
                    MedValue=tanh(MedValue);
                case 'selu'
                    alpha = 1.6732632423543772848170429916717;
                    scale = 1.0507009873554804934193349852946;
                    [r,c]=size(MedValue);
                    for m=1:r
                        for n=1:c
                            if(MedValue(m,n)>0)
                                MedValue(m,n)=scale*MedValue(m,n);
                            else
                                MedValue(m,n)=scale*(alpha*(exp(MedValue(m,n))-1));
                            end
                        end
                    end
            end
    end
end
%policymodel的输出层激活函数为sigmoid 输出在0~1之间 对应的实际动作是-0.5~0.5之间
Q=MedValue;
end