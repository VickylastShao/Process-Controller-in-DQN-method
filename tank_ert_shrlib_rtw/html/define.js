function CodeDefine() { 
this.def = new Array();
this.def["rt_OneStep"] = {file: "ert_main_c.html",line:39,type:"fcn"};
this.def["main"] = {file: "ert_main_c.html",line:76,type:"fcn"};
this.def["Timedelay"] = {file: "tank_c.html",line:26,type:"var"};
this.def["buttomarea"] = {file: "tank_c.html",line:29,type:"var"};
this.def["heightoftank"] = {file: "tank_c.html",line:35,type:"var"};
this.def["maxinflow"] = {file: "tank_c.html",line:38,type:"var"};
this.def["outpipcrosssection"] = {file: "tank_c.html",line:41,type:"var"};
this.def["tank_B"] = {file: "tank_c.html",line:46,type:"var"};
this.def["tank_X"] = {file: "tank_c.html",line:49,type:"var"};
this.def["tank_DW"] = {file: "tank_c.html",line:52,type:"var"};
this.def["tank_U"] = {file: "tank_c.html",line:55,type:"var"};
this.def["tank_Y"] = {file: "tank_c.html",line:58,type:"var"};
this.def["tank_M_"] = {file: "tank_c.html",line:61,type:"var"};
this.def["tank_M"] = {file: "tank_c.html",line:62,type:"var"};
this.def["rt_TDelayInterpolate"] = {file: "tank_c.html",line:73,type:"fcn"};
this.def["rt_ertODEUpdateContinuousStates"] = {file: "tank_c.html",line:251,type:"fcn"};
this.def["tank_step"] = {file: "tank_c.html",line:329,type:"fcn"};
this.def["tank_derivatives"] = {file: "tank_c.html",line:490,type:"fcn"};
this.def["tank_initialize"] = {file: "tank_c.html",line:503,type:"fcn"};
this.def["tank_terminate"] = {file: "tank_c.html",line:584,type:"fcn"};
this.def["B_tank_T"] = {file: "tank_h.html",line:66,type:"type"};
this.def["DW_tank_T"] = {file: "tank_h.html",line:85,type:"type"};
this.def["X_tank_T"] = {file: "tank_h.html",line:91,type:"type"};
this.def["XDot_tank_T"] = {file: "tank_h.html",line:97,type:"type"};
this.def["XDis_tank_T"] = {file: "tank_h.html",line:103,type:"type"};
this.def["ODE3_IntgData"] = {file: "tank_h.html",line:112,type:"type"};
this.def["ExtU_tank_T"] = {file: "tank_h.html",line:119,type:"type"};
this.def["ExtY_tank_T"] = {file: "tank_h.html",line:125,type:"type"};
this.def["P_tank_T"] = {file: "tank_types_h.html",line:27,type:"type"};
this.def["RT_MODEL_tank_T"] = {file: "tank_types_h.html",line:30,type:"type"};
this.def["tank_P"] = {file: "tank_data_c.html",line:26,type:"var"};
this.def["int8_T"] = {file: "rtwtypes_h.html",line:53,type:"type"};
this.def["uint8_T"] = {file: "rtwtypes_h.html",line:54,type:"type"};
this.def["int16_T"] = {file: "rtwtypes_h.html",line:55,type:"type"};
this.def["uint16_T"] = {file: "rtwtypes_h.html",line:56,type:"type"};
this.def["int32_T"] = {file: "rtwtypes_h.html",line:57,type:"type"};
this.def["uint32_T"] = {file: "rtwtypes_h.html",line:58,type:"type"};
this.def["int64_T"] = {file: "rtwtypes_h.html",line:59,type:"type"};
this.def["uint64_T"] = {file: "rtwtypes_h.html",line:60,type:"type"};
this.def["real32_T"] = {file: "rtwtypes_h.html",line:61,type:"type"};
this.def["real64_T"] = {file: "rtwtypes_h.html",line:62,type:"type"};
this.def["real_T"] = {file: "rtwtypes_h.html",line:68,type:"type"};
this.def["time_T"] = {file: "rtwtypes_h.html",line:69,type:"type"};
this.def["boolean_T"] = {file: "rtwtypes_h.html",line:70,type:"type"};
this.def["int_T"] = {file: "rtwtypes_h.html",line:71,type:"type"};
this.def["uint_T"] = {file: "rtwtypes_h.html",line:72,type:"type"};
this.def["ulong_T"] = {file: "rtwtypes_h.html",line:73,type:"type"};
this.def["ulonglong_T"] = {file: "rtwtypes_h.html",line:74,type:"type"};
this.def["char_T"] = {file: "rtwtypes_h.html",line:75,type:"type"};
this.def["uchar_T"] = {file: "rtwtypes_h.html",line:76,type:"type"};
this.def["byte_T"] = {file: "rtwtypes_h.html",line:77,type:"type"};
this.def["pointer_T"] = {file: "rtwtypes_h.html",line:98,type:"type"};
}
CodeDefine.instance = new CodeDefine();
var testHarnessInfo = {OwnerFileName: "", HarnessOwner: "", HarnessName: "", IsTestHarness: "0"};
var relPathToBuildDir = "../ert_main.c";
var fileSep = "\\";
var isPC = true;
function Html2SrcLink() {
	this.html2SrcPath = new Array;
	this.html2Root = new Array;
	this.html2SrcPath["ert_main_c.html"] = "../ert_main.c";
	this.html2Root["ert_main_c.html"] = "ert_main_c.html";
	this.html2SrcPath["tank_c.html"] = "../tank.c";
	this.html2Root["tank_c.html"] = "tank_c.html";
	this.html2SrcPath["tank_h.html"] = "../tank.h";
	this.html2Root["tank_h.html"] = "tank_h.html";
	this.html2SrcPath["tank_private_h.html"] = "../tank_private.h";
	this.html2Root["tank_private_h.html"] = "tank_private_h.html";
	this.html2SrcPath["tank_types_h.html"] = "../tank_types.h";
	this.html2Root["tank_types_h.html"] = "tank_types_h.html";
	this.html2SrcPath["tank_data_c.html"] = "../tank_data.c";
	this.html2Root["tank_data_c.html"] = "tank_data_c.html";
	this.html2SrcPath["rtwtypes_h.html"] = "../rtwtypes.h";
	this.html2Root["rtwtypes_h.html"] = "rtwtypes_h.html";
	this.getLink2Src = function (htmlFileName) {
		 if (this.html2SrcPath[htmlFileName])
			 return this.html2SrcPath[htmlFileName];
		 else
			 return null;
	}
	this.getLinkFromRoot = function (htmlFileName) {
		 if (this.html2Root[htmlFileName])
			 return this.html2Root[htmlFileName];
		 else
			 return null;
	}
}
Html2SrcLink.instance = new Html2SrcLink();
var fileList = [
"ert_main_c.html","tank_c.html","tank_h.html","tank_private_h.html","tank_types_h.html","tank_data_c.html","rtwtypes_h.html"];
