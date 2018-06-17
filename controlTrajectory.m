clc
close all
clear



initialJava();

% 454,4495
% 400,0000

for i=50:70
    DatabaseName='matlab_realtime';

    conn = database(DatabaseName, 'root', '123456', 'com.mysql.jdbc.Driver', ['jdbc:mysql://localhost:3306/',DatabaseName]);

    TableName='history';

    sqlstr=['select * from matlab_realtime.',TableName,' where myindex > ',num2str(i),'0000 and myindex < ',num2str(i+1),'0000 order by myindex '];

    curs = exec(conn, sqlstr);
    curs = fetch(curs);

    cTData=cell2mat(curs.Data);

    close(curs);
    cTData(1,:)=[];

    figure
    plot(cTData(:,2));
    hold on
    plot(cTData(:,3));
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