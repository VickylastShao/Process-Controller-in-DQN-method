clc
close all
clear

%% initialize mysql
initialJava();

DatabaseName='matlabrealtime';

conn = database(DatabaseName, 'root', '123456', 'com.mysql.jdbc.Driver', ['jdbc:mysql://localhost:3306/',DatabaseName]);
if(conn.MaxDatabaseConnections==-1)
    ME = MException('initialERR:noSuchSchemas', 'Schema %s not found', DatabaseName);
    throw(ME);
end

initialTablelist={'history','conditionbase'};
stateDim=3;
actionDim=1;
Dims=[stateDim,actionDim];



for i=1:length(initialTablelist)
    if ~isExistTable(conn,initialTablelist{i})
        CreatTableWithNParas(conn,DatabaseName,initialTablelist{i},Dims);
    else
        ClearTable(conn,DatabaseName,initialTablelist{i});
    end
end


close(conn);

%% initialize tankProto.m

libModelPath    = fullfile(pwd, 'tank_ert_shrlib_rtw');
libSimulinkPath = fullfile(matlabroot, 'simulink', 'include');

% need fully qualified path to header file
hfile = fullfile(libModelPath, 'tank.h');

% load library and generate MATLAB prototype file
coder.loadlibrary('tank_win64', hfile, 'includepath', libModelPath, ...
    'includepath', libSimulinkPath,'mfilename', 'tankProto', ...
    'alias', 'tankmylib')

%% Main

if libisloaded('tankmylib')
    unloadlibrary('tankmylib');
    loadlibrary('tank_win64', 'tankProto', 'alias', 'tankmylib');
end

% �鿴���п��ź��������
% libfunctionsview('tankmylib');
libfunctions('tankmylib', '-full');

% ��ȡ����ָ��
tank_Y  = calllib('tankmylib', 'tank_Y');
tank_U  = calllib('tankmylib', 'tank_U');
buttomarea = calllib('tankmylib', 'buttomarea');
heightoftank = calllib('tankmylib', 'heightoftank');
maxinflow = calllib('tankmylib', 'maxinflow');
outpipcrosssection = calllib('tankmylib', 'outpipcrosssection');
Timedelay = calllib('tankmylib', 'Timedelay');

setdatatype(buttomarea, 'doublePtr', 1, 1);
setdatatype(heightoftank, 'doublePtr', 1, 1);
setdatatype(maxinflow, 'doublePtr', 1, 1);
setdatatype(outpipcrosssection, 'doublePtr', 1, 1);
setdatatype(Timedelay, 'doublePtr', 1, 1);

% ���ó�ʼ������
calllib('tankmylib', 'tank_initialize');
tank_U.Value.In1=0;

buttomarea.Value=1;
heightoftank.Value=2;
maxinflow.Value=0.5;
outpipcrosssection.Value=0.05;
Timedelay.Value=0;


sigma=0.3;% randomPolicy sigma

episode=9000;% ��������

figure();

set(gcf,'position',[30,550,1600,400]); 

myindex=1;

conditionCFG=GetconditionCFG();
dataExistinOneCell=zeros(conditionCFG.s1_cellNum,conditionCFG.s2_cellNum,conditionCFG.s3_cellNum,conditionCFG.a1_cellNum);

decisionCycle=10;

I=0;
while(true)
    tic;   
   
%     readytocollect=Getreadytocollect();
%     
%     if readytocollect==1
        
%         I = I + 1;
%         
%         disp(num2str(I));
%         % ���Է����仯
%         turningpoint=500;
%         if I>turningpoint
%             buttomarea.Value=1;
%             heightoftank.Value=2;
%             maxinflow.Value=0.5;
%             outpipcrosssection.Value=0.05;
%             Timedelay.Value=1;
%             %         0+(I-turningpoint)*0.001;
%         end
        % ���Է����仯
        
        [jsonModel,jsonWeight]=GetPolicyModel();
        
        
        dataExistinOneCelljson=GetdataExistinOneCell();
        conditionCFG=GetconditionCFG();
        
        for i1=1:conditionCFG.s1_cellNum
            for i2=1:conditionCFG.s2_cellNum
                for i3=1:conditionCFG.s3_cellNum
                    for i4=1:conditionCFG.a1_cellNum
                        dataExistinOneCell(i1,i2,i3,i4)=dataExistinOneCelljson.dataExistinOneCell{i1,1}((i2-1)*conditionCFG.s3_cellNum+i3,i4);
                    end
                end
            end
        end
        
        disp(' ');
        disp(['Total Empty Cell Number : ',num2str(sum(sum(sum(sum(dataExistinOneCell==0)))))]);
        disp(' ');
        newCondtion=zeros(episode-1,1)-0.5;
        
        
        Qstate=zeros(episode-1,stateDim);
        Qaction=zeros(episode-1,actionDim);
        NextQstate=zeros(episode-1,stateDim);
        
        
        i=1;
        while(i<episode)
            
            if i==1
                levelSet=1;
                %         if i<=4000
                %             levelSet=sin(i/4000*2*2*pi)/2+1;
            else
                if rem(i,300)==0
                    levelSet=rand()+0.5;% �����0.5~1.5
                end
            end
            
            state=[levelSet tank_Y.Value.Out1 tank_Y.Value.Out2];
            Qstate(i,:)=state;
            inputstate=levelSet;
            
            if i<8000
                %         if i<3000 || (i>=4000 && i<8500)
                indexNow=[-1,-1,-1];
                if(state(1)>=conditionCFG.s1_From...
                        && state(1)<=conditionCFG.s1_to...
                        && state(2)>=conditionCFG.s2_From...
                        && state(2)<=conditionCFG.s2_to...
                        && state(3)>=conditionCFG.s3_From...
                        && state(3)<=conditionCFG.s3_to)
                    indexNow=[
                        floor((state(1)-conditionCFG.s1_From)/((conditionCFG.s1_to-conditionCFG.s1_From)/conditionCFG.s1_cellNum))+1
                        floor((state(2)-conditionCFG.s2_From)/((conditionCFG.s2_to-conditionCFG.s2_From)/conditionCFG.s2_cellNum))+1
                        floor((state(3)-conditionCFG.s3_From)/((conditionCFG.s3_to-conditionCFG.s3_From)/conditionCFG.s3_cellNum))+1
                        ];
                    if indexNow(1)>conditionCFG.s1_cellNum
                        indexNow(1)=conditionCFG.s1_cellNum;
                    end
                    if indexNow(2)>conditionCFG.s2_cellNum
                        indexNow(2)=conditionCFG.s2_cellNum;
                    end
                    if indexNow(3)>conditionCFG.s3_cellNum
                        indexNow(3)=conditionCFG.s3_cellNum;
                    end
                    
                    
                    actionCell=zeros(conditionCFG.a1_cellNum,1);
                    for temp=1:conditionCFG.a1_cellNum
                        actionCell(temp)=dataExistinOneCell(indexNow(1),indexNow(2),indexNow(3),temp);
                    end
                    zerosIndex=find(actionCell==0);
                    if(~isempty(zerosIndex))
                        %����������иù������ڶ�������û���� �Ǿ��ڸö�������������ɶ���
                        randomIndex=zerosIndex(randperm(length(zerosIndex),1));% �ӿ�cell�������ѡ��һ��
                        
                        randomStart=(randomIndex-1)*((conditionCFG.a1_to-conditionCFG.a1_From)/conditionCFG.a1_cellNum)+conditionCFG.a1_From;
                        randomEnd=randomIndex*((conditionCFG.a1_to-conditionCFG.a1_From)/conditionCFG.a1_cellNum)+conditionCFG.a1_From;
                        RandomPolicy=rand*(randomEnd-randomStart)+randomStart;
                        
                        newCondtion(i)=0;
                    else
                        %����������иù���ȫ������������ �Ǿ������Ŷ�������������ɶ���
                        BestPolicy=NNPolicyFun(state,jsonModel,jsonWeight);
                        RandomPolicy = normrnd(BestPolicy,sigma);
                    end
                else
                    %����ù����ڹ����ⷶΧ���� �Ǿ������Ŷ�������������ɶ���
                    BestPolicy=NNPolicyFun(state,jsonModel,jsonWeight);
                    RandomPolicy = normrnd(BestPolicy,sigma);
                end
            else
                %���Ų���
                BestPolicy=NNPolicyFun(state,jsonModel,jsonWeight);
                RandomPolicy = BestPolicy;
                newCondtion(i)=-1;
            end
            
            Qaction(i,:)=RandomPolicy;
            tank_U.Value.In1 = RandomPolicy;
            calllib('tankmylib', 'tank_step');
            nextstate=[inputstate tank_Y.Value.Out1 tank_Y.Value.Out2];
            NextQstate(i,:)=nextstate;
            i=i+1;
        end
        
        
        plot(Qaction,'y','LineWidth',0.5);
        hold on;
        plot(Qstate(:,1),'b','LineWidth',1);
        plot(Qstate(:,2),'r','LineWidth',1);
        plot(Qstate(:,3),'g','LineWidth',1);
        
        plot(newCondtion,'k','LineWidth',0.5);
        
        legend('Action','Order','Current Level','inlet Mass Flow');
        
        hold off;
        
        axis([0,episode,-0.7,2.2]);
        
        pause(0.1);
        
        conn = database(DatabaseName, 'root', '123456', 'com.mysql.jdbc.Driver', ['jdbc:mysql://localhost:3306/',DatabaseName]);
        myindex=SaveData(conn,[Qstate,Qaction,NextQstate],'history',myindex);
        close(conn);
        
%     end
                
    TC=toc;
    
    delayTime=decisionCycle-TC;
    
    if(delayTime>0)
        pause(delayTime);
    end
    
end

%% Functions
function initialJava()
try
    allJavaPath=javaclasspath; %�������java��·��
    %�ѵ�ǰ�ļ�����������ļ��У��Լ����ļ��У�����ӵ�·���
    addpath(genpath(fileparts(mfilename('fullpath'))));
    mysqlDriverPath=which('mysql-connector-java-5.1.45-bin.jar');
    
    %�жϵ�ǰ·�����Ƿ��и������ļ�
    if isempty(mysqlDriverPath)
        errordlg({'�Ҳ���MySQL���ݿ������ļ���mysql-connector-java-5.1.45-bin.jar������ϵ����Ա��','�Ҳ���MySQL���ݿ�����'},'���ݿ���������');
        return;
    end
    
    if ~ismember(mysqlDriverPath,allJavaPath) %�жϸ������Ƿ��Ѿ���·����
        javaaddpath(mysqlDriverPath);
    end
    
catch exception
    errordlg({'������װ���ɹ�,�����ֶ��������MySQL����,�鿴�������´�����ʾ��',exception.identifier},'���ݿ���������');
    return;
end
end

% (conn,[Qstate,Qaction,NextQstate],'history',myindex);


function myindex=SaveData(conn,Data,TableName,myindex)
[r,c]=size(Data);
for i=1:r
    sqlstr=['insert into matlabrealtime.',TableName,' value (',num2str(myindex)]; 
    for j=1:c
        sqlstr=[sqlstr,',',num2str(Data(i,j))];
    end    
    sqlstr=[sqlstr,')'];    
    curs = exec(conn, sqlstr);
    curs = fetch(curs);
    myindex=myindex+1;
end
close(curs);
disp(' ');
disp([datestr(now,13),'    ',TableName, '    Data is Saved']);
end


function CreatTableWithNParas(conn,BaseName,TableName,Dims)
sqlstr=['CREATE TABLE ',BaseName,'.',TableName,' (myindex INT NULL,'];

% state
for i=1:Dims(1)    
    sqlstr=[sqlstr,'s',num2str(i), ' FLOAT NULL,'];    
end

% action
for i=1:Dims(2)    
    sqlstr=[sqlstr,'a',num2str(i), ' FLOAT NULL,'];    
end

% nextstate
for i=1:Dims(1)
    sqlstr=[sqlstr,'ns',num2str(i), ' FLOAT NULL,'];    
end
sqlstr(end)=')';

curs = exec(conn, sqlstr);
curs = fetch(curs);
close(curs);
end


function ClearTable(conn,BaseName,TableNam)
sqlstr=['delete from ',BaseName,'.',TableNam];
curs = exec(conn, sqlstr);
curs = fetch(curs);
close(curs);
end


function result=isExistTable(conn,TableName)
sqlstr=['show tables like ''',TableName,''''];
curs = exec(conn, sqlstr);
curs = fetch(curs);
if strcmp(curs.Data{1,1},TableName)
    result=true;
else
    result=false;
end
close(curs);
end

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
function reture_readytocollect=Getreadytocollect()
while(true)
    try
        addpath(genpath([pwd,'\jsonlab-1.5']));        
        readytocollect=loadjson('readytocollect.json');
        reture_readytocollect=readytocollect.readytocollect;        
        break;
    catch
        disp(' ');
        disp(' try to reload readytocollect');
    end
end
end

function dataExistinOneCell=GetdataExistinOneCell()
while(true)
    try
        addpath(genpath([pwd,'\jsonlab-1.5']));        
        dataExistinOneCell=loadjson('dataExistinOneCell.json');        
        break;
    catch
        disp(' ');
        disp(' try to reload dataExistinOneCell');
    end
end
end

function conditionCFG=GetconditionCFG()
while(true)
    try
        addpath(genpath([pwd,'\jsonlab-1.5']));        
        conditionCFG=loadjson('conditionCFG.json');        
        break;
    catch
        disp(' ');
        disp(' try to reload conditionCFG');
    end
end
end

function Policy=NNPolicyFun(input,jsonModel,jsonWeight)
    [inputSize,~]=size(jsonWeight{1});    
    if(length(input)~=inputSize)
        Policy=0;
    else        
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
        %policymodel������㼤���Ϊsigmoid �����0~1֮�� ��Ӧ��ʵ�ʶ�����-0.5~0.5֮��
        Policy=MedValue-0.5;
    end    
end

%% simulink code lib
% libModelPath    = fullfile(pwd, 'tank_ert_shrlib_rtw');
% libSimulinkPath = fullfile(matlabroot, 'simulink', 'include');
%
% % need fully qualified path to header file
% hfile = fullfile(libModelPath, 'tank.h');

% load library and generate MATLAB prototype file
% coder.loadlibrary('tank_win64', hfile, 'includepath', libModelPath, ...
%     'includepath', libSimulinkPath,'mfilename', 'tankProto', ...
%     'alias', 'tankmylib')

% % unloadlibrary('testmylib')
%
% �м����
% k  = calllib('tankmylib', 'k');
% setdatatype(   k, 'doublePtr', 1, 1)


% % ��ȡָ��
% test_U  = calllib('testmylib', 'test_U');
% setdatatype(test_U, 'doublePtr')
% test_U.Value = 1000;
%
% % ָ��ָ���ά�Ⱥ�����
% % setdatatype(test_U, 'doublePtr', 1, 1)
%
% % �鿴ָ��Ĭ��ֵ
% % disp(['Default test_U is : ' num2str(test_U.Value)]);
%
% % ����ָ��ֵ
% % test_U.Value = 1000;
% %
% % % �鿴ָ��ֵ
% % disp(['New test_U is : ' num2str(test_U.Value)]);
%
% struct.test_U = 4;
% % ����ģ��
% anOutput = calllib('testmylib', 'test_step',struct);
%
% % �鿴���
% disp(anOutput);
