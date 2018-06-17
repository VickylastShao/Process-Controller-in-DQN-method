/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: tank.h
 *
 * Code generated for Simulink model 'tank'.
 *
 * Model version                  : 1.67
 * Simulink Coder version         : 8.13 (R2017b) 24-Jul-2017
 * C/C++ source code generated on : Thu May 24 15:31:56 2018
 *
 * Target selection: ert_shrlib.tlc
 * Embedded hardware selection: 32-bit Generic
 * Emulation hardware selection:
 *    Differs from embedded hardware (MATLAB Host)
 * Code generation objectives: Unspecified
 * Validation result: Not run
 */

#ifndef RTW_HEADER_tank_h_
#define RTW_HEADER_tank_h_
#include <float.h>
#include <math.h>
#include <string.h>
#ifndef tank_COMMON_INCLUDES_
# define tank_COMMON_INCLUDES_
#include "rtwtypes.h"
#include "rtw_continuous.h"
#include "rtw_solver.h"
#endif                                 /* tank_COMMON_INCLUDES_ */

#include "tank_types.h"

/* Macros for accessing real-time model data structure */
#ifndef rtmGetErrorStatus
# define rtmGetErrorStatus(rtm)        ((rtm)->errorStatus)
#endif

#ifndef rtmSetErrorStatus
# define rtmSetErrorStatus(rtm, val)   ((rtm)->errorStatus = (val))
#endif

#ifndef rtmGetStopRequested
# define rtmGetStopRequested(rtm)      ((rtm)->Timing.stopRequestedFlag)
#endif

#ifndef rtmSetStopRequested
# define rtmSetStopRequested(rtm, val) ((rtm)->Timing.stopRequestedFlag = (val))
#endif

#ifndef rtmGetStopRequestedPtr
# define rtmGetStopRequestedPtr(rtm)   (&((rtm)->Timing.stopRequestedFlag))
#endif

#ifndef rtmGetT
# define rtmGetT(rtm)                  (rtmGetTPtr((rtm))[0])
#endif

/* Block signals (auto storage) */
typedef struct {
  real_T tankmaxinflow1;               /* '<Root>/tank max inflow1 最大流量' */
  real_T Fcn;                          /* '<S3>/Fcn' */
  real_T Fcn_i;                        /* '<S4>/Fcn' */
} B_tank_T;

/* Block states (auto storage) for system '<Root>' */
typedef struct {
  struct {
    real_T modelTStart;
    real_T TUbufferArea[2048];
  } TransportDelay_RWORK;              /* '<Root>/Transport Delay' */

  struct {
    void *TUbufferPtrs[2];
  } TransportDelay_PWORK;              /* '<Root>/Transport Delay' */

  struct {
    int_T Tail;
    int_T Head;
    int_T Last;
    int_T CircularBufSize;
  } TransportDelay_IWORK;              /* '<Root>/Transport Delay' */
} DW_tank_T;

/* Continuous states (auto storage) */
typedef struct {
  real_T Integrator_CSTATE;            /* '<S4>/Integrator' */
  real_T Integrator_CSTATE_i;          /* '<S3>/Integrator' */
} X_tank_T;

/* State derivatives (auto storage) */
typedef struct {
  real_T Integrator_CSTATE;            /* '<S4>/Integrator' */
  real_T Integrator_CSTATE_i;          /* '<S3>/Integrator' */
} XDot_tank_T;

/* State disabled  */
typedef struct {
  boolean_T Integrator_CSTATE;         /* '<S4>/Integrator' */
  boolean_T Integrator_CSTATE_i;       /* '<S3>/Integrator' */
} XDis_tank_T;

#ifndef ODE3_INTG
#define ODE3_INTG

/* ODE3 Integration Data */
typedef struct {
  real_T *y;                           /* output */
  real_T *f[3];                        /* derivatives */
} ODE3_IntgData;

#endif

/* External inputs (root inport signals with auto storage) */
typedef struct {
  real_T In1;                          /* '<Root>/In1' */
} ExtU_tank_T;

/* External outputs (root outports fed by signals with auto storage) */
typedef struct {
  real_T Out1;                         /* '<Root>/Out1' */
  real_T Out2;                         /* '<Root>/Out2' */
} ExtY_tank_T;

/* Parameters (auto storage) */
struct P_tank_T_ {
  real_T Subsystem1_InitialPosition;   /* Mask Parameter: Subsystem1_InitialPosition
                                        * Referenced by: '<S3>/Integrator'
                                        */
  real_T tank1_initialHt;              /* Mask Parameter: tank1_initialHt
                                        * Referenced by: '<S4>/Integrator'
                                        */
  real_T tankvolume_lb;                /* Mask Parameter: tankvolume_lb
                                        * Referenced by: '<S4>/Saturation'
                                        */
  real_T LimitedIntegrator_lb;         /* Mask Parameter: LimitedIntegrator_lb
                                        * Referenced by: '<S3>/Saturation'
                                        */
  real_T LimitedIntegrator_ub;         /* Mask Parameter: LimitedIntegrator_ub
                                        * Referenced by: '<S3>/Saturation'
                                        */
  real_T TransportDelay_InitOutput;    /* Expression: 0
                                        * Referenced by: '<Root>/Transport Delay'
                                        */
};

/* Real-time Model Data Structure */
struct tag_RTM_tank_T {
  const char_T *errorStatus;
  RTWSolverInfo solverInfo;
  X_tank_T *contStates;
  int_T *periodicContStateIndices;
  real_T *periodicContStateRanges;
  real_T *derivs;
  boolean_T *contStateDisabled;
  boolean_T zCCacheNeedsReset;
  boolean_T derivCacheNeedsReset;
  boolean_T CTOutputIncnstWithState;
  real_T odeY[2];
  real_T odeF[3][2];
  ODE3_IntgData intgData;

  /*
   * Sizes:
   * The following substructure contains sizes information
   * for many of the model attributes such as inputs, outputs,
   * dwork, sample times, etc.
   */
  struct {
    int_T numContStates;
    int_T numPeriodicContStates;
    int_T numSampTimes;
  } Sizes;

  /*
   * Timing:
   * The following substructure contains information regarding
   * the timing information for the model.
   */
  struct {
    uint32_T clockTick0;
    time_T stepSize0;
    uint32_T clockTick1;
    SimTimeStep simTimeStep;
    boolean_T stopRequestedFlag;
    time_T *t;
    time_T tArray[2];
  } Timing;
};

/* Block parameters (auto storage) */
extern P_tank_T tank_P;

/* Block signals (auto storage) */
extern B_tank_T tank_B;

/* Continuous states (auto storage) */
extern X_tank_T tank_X;

/* Block states (auto storage) */
extern DW_tank_T tank_DW;

/* External inputs (root inport signals with auto storage) */
extern ExtU_tank_T tank_U;

/* External outputs (root outports fed by signals with auto storage) */
extern ExtY_tank_T tank_Y;

/*
 * Exported Global Parameters
 *
 * Note: Exported global parameters are tunable parameters with an exported
 * global storage class designation.  Code generation will declare the memory for
 * these parameters and exports their symbols.
 *
 */
extern real_T Timedelay;               /* Variable: Timedelay
                                        * Referenced by: '<Root>/Transport Delay'
                                        */
extern real_T buttomarea;              /* Variable: buttomarea
                                        * Referenced by:
                                        *   '<S2>/1//area'
                                        *   '<S4>/Integrator'
                                        *   '<S4>/Saturation'
                                        */
extern real_T heightoftank;            /* Variable: heightoftank
                                        * Referenced by: '<S4>/Saturation'
                                        */
extern real_T maxinflow;               /* Variable: maxinflow
                                        * Referenced by: '<Root>/tank max inflow1 最大流量'
                                        */
extern real_T outpipcrosssection;      /* Variable: outpipcrosssection
                                        * Referenced by: '<S2>/outletArea'
                                        */

/* Model entry point functions */
extern void tank_initialize(void);
extern void tank_step(void);
extern void tank_terminate(void);

/* Real-time Model object */
extern RT_MODEL_tank_T *const tank_M;

/*-
 * These blocks were eliminated from the model due to optimizations:
 *
 * Block '<S2>/Overflow sensor' : Unused code path elimination
 */

/*-
 * The generated code includes comments that allow you to trace directly
 * back to the appropriate location in the model.  The basic format
 * is <system>/block_name, where system is the system number (uniquely
 * assigned by Simulink) and block_name is the name of the block.
 *
 * Use the MATLAB hilite_system command to trace the generated code back
 * to the model.  For example,
 *
 * hilite_system('<S3>')    - opens system 3
 * hilite_system('<S3>/Kp') - opens and selects block Kp which resides in S3
 *
 * Here is the system hierarchy for this model
 *
 * '<Root>' : 'tank'
 * '<S1>'   : 'tank/Subsystem1'
 * '<S2>'   : 'tank/tank 1'
 * '<S3>'   : 'tank/Subsystem1/Limited Integrator'
 * '<S4>'   : 'tank/tank 1/tank volume'
 */
#endif                                 /* RTW_HEADER_tank_h_ */

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
