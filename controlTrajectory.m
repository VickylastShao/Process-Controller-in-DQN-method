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
    allJavaPath=javaclasspath; %获得所有java的路径
    %把当前文件夹里的所有文件夹（以及子文件夹）都添加到路径里；
    addpath(genpath(fileparts(mfilename('fullpath'))));
    mysqlDriverPath=which('mysql-connector-java-5.1.45-bin.jar');
    
    %判断当前路径下是否有该驱动文件
    if isempty(mysqlDriverPath)
        errordlg({'找不到MySQL数据库驱动文件：mysql-connector-java-5.1.45-bin.jar，请联系管理员！','找不到MySQL数据库驱动'},'数据库驱动错误');
        return;
    end
    
    if ~ismember(mysqlDriverPath,allJavaPath) %判断该驱动是否已经在路径里
        javaaddpath(mysqlDriverPath);
    end
    
catch exception
    errordlg({'驱动安装不成功,尝试手动添加驱动MySQL驱动,查看命令行下错误提示！',exception.identifier},'数据库驱动错误');
    return;
end
end