/*
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * File: tank_data.c
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

/* Block parameters (auto storage) */
P_tank_T tank_P = {
  /* Mask Parameter: Subsystem1_InitialPosition
   * Referenced by: '<S3>/Integrator'
   */
  0.0,

  /* Mask Parameter: tank1_initialHt
   * Referenced by: '<S4>/Integrator'
   */
  0.5,

  /* Mask Parameter: tankvolume_lb
   * Referenced by: '<S4>/Saturation'
   */
  0.0,

  /* Mask Parameter: LimitedIntegrator_lb
   * Referenced by: '<S3>/Saturation'
   */
  0.0,

  /* Mask Parameter: LimitedIntegrator_ub
   * Referenced by: '<S3>/Saturation'
   */
  1.0,

  /* Expression: 0
   * Referenced by: '<Root>/Transport Delay'
   */
  0.0
};

/*
 * File trailer for generated code.
 *
 * [EOF]
 */
