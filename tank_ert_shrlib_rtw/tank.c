/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: tank.c
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

#include "tank.h"
#include "tank_private.h"

/* Exported block parameters */
real_T Timedelay = 0.0;                /* Variable: Timedelay
                                        * Referenced by: '<Root>/Transport Delay'
                                        */
real_T buttomarea = 1.0;               /* Variable: buttomarea
                                        * Referenced by:
                                        *   '<S2>/1//area'
                                        *   '<S4>/Integrator'
                                        *   '<S4>/Saturation'
                                        */
real_T heightoftank = 2.0;             /* Variable: heightoftank
                                        * Referenced by: '<S4>/Saturation'
                                        */
real_T maxinflow = 0.5;                /* Variable: maxinflow
                                        * Referenced by: '<Root>/tank max inflow1 最大流量'
                                        */
real_T outpipcrosssection = 0.05;      /* Variable: outpipcrosssection
                                        * Referenced by: '<S2>/outletArea'
                                        */

/* Block signals (auto storage) */
B_tank_T tank_B;

/* Continuous states */
X_tank_T tank_X;

/* Block states (auto storage) */
DW_tank_T tank_DW;

/* External inputs (root inport signals with auto storage) */
ExtU_tank_T tank_U;

/* External outputs (root outports fed by signals with auto storage) */
ExtY_tank_T tank_Y;

/* Real-time model */
RT_MODEL_tank_T tank_M_;
RT_MODEL_tank_T *const tank_M = &tank_M_;

/*
 * Time delay interpolation routine
 *
 * The linear interpolation is performed using the formula:
 *
 *          (t2 - tMinusDelay)         (tMinusDelay - t1)
 * u(t)  =  ----------------- * u1  +  ------------------- * u2
 *              (t2 - t1)                  (t2 - t1)
 */
real_T rt_TDelayInterpolate(
  real_T tMinusDelay,                  /* tMinusDelay = currentSimTime - delay */
  real_T tStart,
  real_T *tBuf,
  real_T *uBuf,
  int_T bufSz,
  int_T *lastIdx,
  int_T oldestIdx,
  int_T newIdx,
  real_T initOutput,
  boolean_T discrete,
  boolean_T minorStepAndTAtLastMajorOutput)
{
  int_T i;
  real_T yout, t1, t2, u1, u2;

  /*
   * If there is only one data point in the buffer, this data point must be
   * the t= 0 and tMinusDelay > t0, it ask for something unknown. The best
   * guess if initial output as well
   */
  if ((newIdx == 0) && (oldestIdx ==0 ) && (tMinusDelay > tStart))
    return initOutput;

  /*
   * If tMinusDelay is less than zero, should output initial value
   */
  if (tMinusDelay <= tStart)
    return initOutput;

  /* For fixed buffer extrapolation:
   * if tMinusDelay is small than the time at oldestIdx, if discrete, output
   * tailptr value,  else use tailptr and tailptr+1 value to extrapolate
   * It is also for fixed buffer. Note: The same condition can happen for transport delay block where
   * use tStart and and t[tail] other than using t[tail] and t[tail+1].
   * See below
   */
  if ((tMinusDelay <= tBuf[oldestIdx] ) ) {
    if (discrete) {
      return(uBuf[oldestIdx]);
    } else {
      int_T tempIdx= oldestIdx + 1;
      if (oldestIdx == bufSz-1)
        tempIdx = 0;
      t1= tBuf[oldestIdx];
      t2= tBuf[tempIdx];
      u1= uBuf[oldestIdx];
      u2= uBuf[tempIdx];
      if (t2 == t1) {
        if (tMinusDelay >= t2) {
          yout = u2;
        } else {
          yout = u1;
        }
      } else {
        real_T f1 = (t2-tMinusDelay) / (t2-t1);
        real_T f2 = 1.0 - f1;

        /*
         * Use Lagrange's interpolation formula.  Exact outputs at t1, t2.
         */
        yout = f1*u1 + f2*u2;
      }

      return yout;
    }
  }

  /*
   * When block does not have direct feedthrough, we use the table of
   * values to extrapolate off the end of the table for delays that are less
   * than 0 (less then step size).  This is not completely accurate.  The
   * chain of events is as follows for a given time t.  Major output - look
   * in table.  Update - add entry to table.  Now, if we call the output at
   * time t again, there is a new entry in the table. For very small delays,
   * this means that we will have a different answer from the previous call
   * to the output fcn at the same time t.  The following code prevents this
   * from happening.
   */
  if (minorStepAndTAtLastMajorOutput) {
    /* pretend that the new entry has not been added to table */
    if (newIdx != 0) {
      if (*lastIdx == newIdx) {
        (*lastIdx)--;
      }

      newIdx--;
    } else {
      if (*lastIdx == newIdx) {
        *lastIdx = bufSz-1;
      }

      newIdx = bufSz - 1;
    }
  }

  i = *lastIdx;
  if (tBuf[i] < tMinusDelay) {
    /* Look forward starting at last index */
    while (tBuf[i] < tMinusDelay) {
      /* May occur if the delay is less than step-size - extrapolate */
      if (i == newIdx)
        break;
      i = ( i < (bufSz-1) ) ? (i+1) : 0;/* move through buffer */
    }
  } else {
    /*
     * Look backwards starting at last index which can happen when the
     * delay time increases.
     */
    while (tBuf[i] >= tMinusDelay) {
      /*
       * Due to the entry condition at top of function, we
       * should never hit the end.
       */
      i = (i > 0) ? i-1 : (bufSz-1);   /* move through buffer */
    }

    i = ( i < (bufSz-1) ) ? (i+1) : 0;
  }

  *lastIdx = i;
  if (discrete) {
    /*
     * tempEps = 128 * eps;
     * localEps = max(tempEps, tempEps*fabs(tBuf[i]))/2;
     */
    double tempEps = (DBL_EPSILON) * 128.0;
    double localEps = tempEps * fabs(tBuf[i]);
    if (tempEps > localEps) {
      localEps = tempEps;
    }

    localEps = localEps / 2.0;
    if (tMinusDelay >= (tBuf[i] - localEps)) {
      yout = uBuf[i];
    } else {
      if (i == 0) {
        yout = uBuf[bufSz-1];
      } else {
        yout = uBuf[i-1];
      }
    }
  } else {
    if (i == 0) {
      t1 = tBuf[bufSz-1];
      u1 = uBuf[bufSz-1];
    } else {
      t1 = tBuf[i-1];
      u1 = uBuf[i-1];
    }

    t2 = tBuf[i];
    u2 = uBuf[i];
    if (t2 == t1) {
      if (tMinusDelay >= t2) {
        yout = u2;
      } else {
        yout = u1;
      }
    } else {
      real_T f1 = (t2-tMinusDelay) / (t2-t1);
      real_T f2 = 1.0 - f1;

      /*
       * Use Lagrange's interpolation formula.  Exact outputs at t1, t2.
       */
      yout = f1*u1 + f2*u2;
    }
  }

  return(yout);
}

/*
 * This function updates continuous states using the ODE3 fixed-step
 * solver algorithm
 */
static void rt_ertODEUpdateContinuousStates(RTWSolverInfo *si )
{
  /* Solver Matrices */
  static const real_T rt_ODE3_A[3] = {
    1.0/2.0, 3.0/4.0, 1.0
  };

  static const real_T rt_ODE3_B[3][3] = {
    { 1.0/2.0, 0.0, 0.0 },

    { 0.0, 3.0/4.0, 0.0 },

    { 2.0/9.0, 1.0/3.0, 4.0/9.0 }
  };

  time_T t = rtsiGetT(si);
  time_T tnew = rtsiGetSolverStopTime(si);
  time_T h = rtsiGetStepSize(si);
  real_T *x = rtsiGetContStates(si);
  ODE3_IntgData *id = (ODE3_IntgData *)rtsiGetSolverData(si);
  real_T *y = id->y;
  real_T *f0 = id->f[0];
  real_T *f1 = id->f[1];
  real_T *f2 = id->f[2];
  real_T hB[3];
  int_T i;
  int_T nXc = 2;
  rtsiSetSimTimeStep(si,MINOR_TIME_STEP);

  /* Save the state values at time t in y, we'll use x as ynew. */
  (void) memcpy(y, x,
                (uint_T)nXc*sizeof(real_T));

  /* Assumes that rtsiSetT and ModelOutputs are up-to-date */
  /* f0 = f(t,y) */
  rtsiSetdX(si, f0);
  tank_derivatives();

  /* f(:,2) = feval(odefile, t + hA(1), y + f*hB(:,1), args(:)(*)); */
  hB[0] = h * rt_ODE3_B[0][0];
  for (i = 0; i < nXc; i++) {
    x[i] = y[i] + (f0[i]*hB[0]);
  }

  rtsiSetT(si, t + h*rt_ODE3_A[0]);
  rtsiSetdX(si, f1);
  tank_step();
  tank_derivatives();

  /* f(:,3) = feval(odefile, t + hA(2), y + f*hB(:,2), args(:)(*)); */
  for (i = 0; i <= 1; i++) {
    hB[i] = h * rt_ODE3_B[1][i];
  }

  for (i = 0; i < nXc; i++) {
    x[i] = y[i] + (f0[i]*hB[0] + f1[i]*hB[1]);
  }

  rtsiSetT(si, t + h*rt_ODE3_A[1]);
  rtsiSetdX(si, f2);
  tank_step();
  tank_derivatives();

  /* tnew = t + hA(3);
     ynew = y + f*hB(:,3); */
  for (i = 0; i <= 2; i++) {
    hB[i] = h * rt_ODE3_B[2][i];
  }

  for (i = 0; i < nXc; i++) {
    x[i] = y[i] + (f0[i]*hB[0] + f1[i]*hB[1] + f2[i]*hB[2]);
  }

  rtsiSetT(si, tnew);
  rtsiSetSimTimeStep(si,MAJOR_TIME_STEP);
}

/* Model step function */
void tank_step(void)
{
  /* local block i/o variables */
  real_T rtb_TransportDelay;
  real_T rtb_uarea;
  real_T rtb_sum;
  if (rtmIsMajorTimeStep(tank_M)) {
    /* set solver stop time */
    rtsiSetSolverStopTime(&tank_M->solverInfo,((tank_M->Timing.clockTick0+1)*
      tank_M->Timing.stepSize0));
  }                                    /* end MajorTimeStep */

  /* Update absolute time of base rate at minor time step */
  if (rtmIsMinorTimeStep(tank_M)) {
    tank_M->Timing.t[0] = rtsiGetT(&tank_M->solverInfo);
  }

  /* Saturate: '<S4>/Saturation' incorporates:
   *  Integrator: '<S4>/Integrator'
   */
  rtb_uarea = heightoftank * buttomarea;
  if (!(tank_X.Integrator_CSTATE > rtb_uarea)) {
    if (tank_X.Integrator_CSTATE < tank_P.tankvolume_lb) {
      rtb_uarea = tank_P.tankvolume_lb;
    } else {
      rtb_uarea = tank_X.Integrator_CSTATE;
    }
  }

  /* End of Saturate: '<S4>/Saturation' */

  /* Gain: '<S2>/1//area' */
  rtb_uarea *= 1.0 / buttomarea;

  /* Outport: '<Root>/Out1' */
  tank_Y.Out1 = rtb_uarea;
  if (rtmIsMajorTimeStep(tank_M)) {
    /* Constant: '<Root>/tank max inflow1 最大流量' */
    tank_B.tankmaxinflow1 = maxinflow;
  }

  /* Saturate: '<S3>/Saturation' incorporates:
   *  Integrator: '<S3>/Integrator'
   */
  if (tank_X.Integrator_CSTATE_i > tank_P.LimitedIntegrator_ub) {
    rtb_sum = tank_P.LimitedIntegrator_ub;
  } else if (tank_X.Integrator_CSTATE_i < tank_P.LimitedIntegrator_lb) {
    rtb_sum = tank_P.LimitedIntegrator_lb;
  } else {
    rtb_sum = tank_X.Integrator_CSTATE_i;
  }

  /* End of Saturate: '<S3>/Saturation' */

  /* Product: '<S1>/Product' */
  rtb_sum *= tank_B.tankmaxinflow1;

  /* Outport: '<Root>/Out2' */
  tank_Y.Out2 = rtb_sum;

  /* TransportDelay: '<Root>/Transport Delay' incorporates:
   *  Inport: '<Root>/In1'
   */
  {
    real_T **uBuffer = (real_T**)&tank_DW.TransportDelay_PWORK.TUbufferPtrs[0];
    real_T **tBuffer = (real_T**)&tank_DW.TransportDelay_PWORK.TUbufferPtrs[1];
    real_T simTime = tank_M->Timing.t[0];
    real_T tMinusDelay = simTime - Timedelay;
    if (Timedelay == 0.0)
      rtb_TransportDelay = tank_U.In1;
    else
      rtb_TransportDelay = rt_TDelayInterpolate(
        tMinusDelay,
        0.0,
        *tBuffer,
        *uBuffer,
        tank_DW.TransportDelay_IWORK.CircularBufSize,
        &tank_DW.TransportDelay_IWORK.Last,
        tank_DW.TransportDelay_IWORK.Tail,
        tank_DW.TransportDelay_IWORK.Head,
        tank_P.TransportDelay_InitOutput,
        0,
        0);
  }

  /* Fcn: '<S3>/Fcn' incorporates:
   *  Integrator: '<S3>/Integrator'
   */
  tank_B.Fcn = (real_T)(((tank_X.Integrator_CSTATE_i > 0.0) +
    (rtb_TransportDelay >= 0.0) > (int32_T)0.0) * ((tank_X.Integrator_CSTATE_i <
    1.0) + (rtb_TransportDelay <= 0.0) > (int32_T)0.0)) * rtb_TransportDelay;

  /* Fcn: '<S2>/sqrt(2gh)' */
  rtb_uarea *= 19.6;
  if (rtb_uarea < 0.0) {
    rtb_uarea = -sqrt(-rtb_uarea);
  } else {
    rtb_uarea = sqrt(rtb_uarea);
  }

  /* End of Fcn: '<S2>/sqrt(2gh)' */

  /* Sum: '<S2>/sum' incorporates:
   *  Gain: '<S2>/outletArea'
   */
  rtb_sum -= outpipcrosssection * rtb_uarea;

  /* Fcn: '<S4>/Fcn' incorporates:
   *  Integrator: '<S4>/Integrator'
   */
  tank_B.Fcn_i = (real_T)(((tank_X.Integrator_CSTATE > 0.0) + (rtb_sum >= 0.0) >
    (int32_T)0.0) * ((tank_X.Integrator_CSTATE < 2.0) + (rtb_sum <= 0.0) >
                     (int32_T)0.0)) * rtb_sum;
  if (rtmIsMajorTimeStep(tank_M)) {
    /* Update for TransportDelay: '<Root>/Transport Delay' incorporates:
     *  Inport: '<Root>/In1'
     */
    {
      real_T **uBuffer = (real_T**)&tank_DW.TransportDelay_PWORK.TUbufferPtrs[0];
      real_T **tBuffer = (real_T**)&tank_DW.TransportDelay_PWORK.TUbufferPtrs[1];
      real_T simTime = tank_M->Timing.t[0];
      tank_DW.TransportDelay_IWORK.Head = ((tank_DW.TransportDelay_IWORK.Head <
        (tank_DW.TransportDelay_IWORK.CircularBufSize-1)) ?
        (tank_DW.TransportDelay_IWORK.Head+1) : 0);
      if (tank_DW.TransportDelay_IWORK.Head == tank_DW.TransportDelay_IWORK.Tail)
      {
        tank_DW.TransportDelay_IWORK.Tail = ((tank_DW.TransportDelay_IWORK.Tail <
          (tank_DW.TransportDelay_IWORK.CircularBufSize-1)) ?
          (tank_DW.TransportDelay_IWORK.Tail+1) : 0);
      }

      (*tBuffer)[tank_DW.TransportDelay_IWORK.Head] = simTime;
      (*uBuffer)[tank_DW.TransportDelay_IWORK.Head] = tank_U.In1;
    }
  }                                    /* end MajorTimeStep */

  if (rtmIsMajorTimeStep(tank_M)) {
    rt_ertODEUpdateContinuousStates(&tank_M->solverInfo);

    /* Update absolute time for base rate */
    /* The "clockTick0" counts the number of times the code of this task has
     * been executed. The absolute time is the multiplication of "clockTick0"
     * and "Timing.stepSize0". Size of "clockTick0" ensures timer will not
     * overflow during the application lifespan selected.
     */
    ++tank_M->Timing.clockTick0;
    tank_M->Timing.t[0] = rtsiGetSolverStopTime(&tank_M->solverInfo);

    {
      /* Update absolute timer for sample time: [0.1s, 0.0s] */
      /* The "clockTick1" counts the number of times the code of this task has
       * been executed. The resolution of this integer timer is 0.1, which is the step size
       * of the task. Size of "clockTick1" ensures timer will not overflow during the
       * application lifespan selected.
       */
      tank_M->Timing.clockTick1++;
    }
  }                                    /* end MajorTimeStep */
}

/* Derivatives for root system: '<Root>' */
void tank_derivatives(void)
{
  XDot_tank_T *_rtXdot;
  _rtXdot = ((XDot_tank_T *) tank_M->derivs);

  /* Derivatives for Integrator: '<S4>/Integrator' */
  _rtXdot->Integrator_CSTATE = tank_B.Fcn_i;

  /* Derivatives for Integrator: '<S3>/Integrator' */
  _rtXdot->Integrator_CSTATE_i = tank_B.Fcn;
}

/* Model initialize function */
void tank_initialize(void)
{
  /* Registration code */

  /* initialize real-time model */
  (void) memset((void *)tank_M, 0,
                sizeof(RT_MODEL_tank_T));

  {
    /* Setup solver object */
    rtsiSetSimTimeStepPtr(&tank_M->solverInfo, &tank_M->Timing.simTimeStep);
    rtsiSetTPtr(&tank_M->solverInfo, &rtmGetTPtr(tank_M));
    rtsiSetStepSizePtr(&tank_M->solverInfo, &tank_M->Timing.stepSize0);
    rtsiSetdXPtr(&tank_M->solverInfo, &tank_M->derivs);
    rtsiSetContStatesPtr(&tank_M->solverInfo, (real_T **) &tank_M->contStates);
    rtsiSetNumContStatesPtr(&tank_M->solverInfo, &tank_M->Sizes.numContStates);
    rtsiSetNumPeriodicContStatesPtr(&tank_M->solverInfo,
      &tank_M->Sizes.numPeriodicContStates);
    rtsiSetPeriodicContStateIndicesPtr(&tank_M->solverInfo,
      &tank_M->periodicContStateIndices);
    rtsiSetPeriodicContStateRangesPtr(&tank_M->solverInfo,
      &tank_M->periodicContStateRanges);
    rtsiSetErrorStatusPtr(&tank_M->solverInfo, (&rtmGetErrorStatus(tank_M)));
    rtsiSetRTModelPtr(&tank_M->solverInfo, tank_M);
  }

  rtsiSetSimTimeStep(&tank_M->solverInfo, MAJOR_TIME_STEP);
  tank_M->intgData.y = tank_M->odeY;
  tank_M->intgData.f[0] = tank_M->odeF[0];
  tank_M->intgData.f[1] = tank_M->odeF[1];
  tank_M->intgData.f[2] = tank_M->odeF[2];
  tank_M->contStates = ((X_tank_T *) &tank_X);
  rtsiSetSolverData(&tank_M->solverInfo, (void *)&tank_M->intgData);
  rtsiSetSolverName(&tank_M->solverInfo,"ode3");
  rtmSetTPtr(tank_M, &tank_M->Timing.tArray[0]);
  tank_M->Timing.stepSize0 = 0.1;

  /* block I/O */
  (void) memset(((void *) &tank_B), 0,
                sizeof(B_tank_T));

  /* states (continuous) */
  {
    (void) memset((void *)&tank_X, 0,
                  sizeof(X_tank_T));
  }

  /* states (dwork) */
  (void) memset((void *)&tank_DW, 0,
                sizeof(DW_tank_T));

  /* external inputs */
  tank_U.In1 = 0.0;

  /* external outputs */
  (void) memset((void *)&tank_Y, 0,
                sizeof(ExtY_tank_T));

  /* Start for TransportDelay: '<Root>/Transport Delay' incorporates:
   *  Inport: '<Root>/In1'
   */
  {
    real_T *pBuffer = &tank_DW.TransportDelay_RWORK.TUbufferArea[0];
    tank_DW.TransportDelay_IWORK.Tail = 0;
    tank_DW.TransportDelay_IWORK.Head = 0;
    tank_DW.TransportDelay_IWORK.Last = 0;
    tank_DW.TransportDelay_IWORK.CircularBufSize = 1024;
    pBuffer[0] = tank_P.TransportDelay_InitOutput;
    pBuffer[1024] = tank_M->Timing.t[0];
    tank_DW.TransportDelay_PWORK.TUbufferPtrs[0] = (void *) &pBuffer[0];
    tank_DW.TransportDelay_PWORK.TUbufferPtrs[1] = (void *) &pBuffer[1024];
  }

  /* InitializeConditions for Integrator: '<S4>/Integrator' */
  tank_X.Integrator_CSTATE = tank_P.tank1_initialHt * buttomarea;

  /* InitializeConditions for Integrator: '<S3>/Integrator' */
  tank_X.Integrator_CSTATE_i = tank_P.Subsystem1_InitialPosition;
}

/* Model terminate function */
void tank_terminate(void)
{
  /* (no terminate code required) */
}

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
