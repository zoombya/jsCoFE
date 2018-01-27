##!/usr/bin/python

#
# ============================================================================
#
#    26.01.18   <--  Date of Last Modification.
#                   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ----------------------------------------------------------------------------
#
#  CCP4EZ Combined Auto-Solver MoRDa module
#
#  Copyright (C) Eugene Krissinel, Andrey Lebedev 2017-2018
#
# ============================================================================
#

import os

#  ccp4-python imports
import pyrvapi
import pyrvapi_ext.parsers

import mtz
import datred_utils

import ccp4ez_simbad12

# ============================================================================

class MoRDa(ccp4ez_simbad12.Simbad12):

    def morda_header_id(self):  return "ccp4ez_morda_header_tab"
    def morda_page_id  (self):  return "ccp4ez_morda_tab"
    def morda_logtab_id(self):  return "ccp4ez_morda_log_tab"
    def morda_errtab_id(self):  return "ccp4ez_morda_err_tab"

    def morda_dir      (self):  return "morda_results"

    # ----------------------------------------------------------------------

    def morda ( self,mtz_branch_id ):

        if not self.seqpath:
            return ""

        self.putWaitMessageLF ( "<b>" + str(self.stage_no+1) +
                                ". Automated Molecular Replacement (MoRDa)</b>" )

        branch_data = self.start_branch ( "Auto-MR",
                        "CCP4ez Automated Structure Solver: Auto-MR with MoRDa",
                        self.morda_dir      (),mtz_branch_id,
                        self.morda_header_id(),self.morda_logtab_id(),
                        self.morda_errtab_id() )

        morda_xyz  = os.path.join ( self.morda_dir(),self.outputname + ".pdb" )
        morda_mtz  = os.path.join ( self.morda_dir(),self.outputname + ".mtz" )
        morda_map  = os.path.join ( self.morda_dir(),self.outputname + ".map" )
        morda_dmap = os.path.join ( self.morda_dir(),self.outputname + "_dmap.pdb" )

        self.flush()
        self.storeReportDocument (
            '{ "jobId"     : "' + self.jobId              + '",' +
            '  "logTabId"  : "' + self.morda_logtab_id()  + '",' +
            '  "name_xyz"  : "' + morda_xyz               + '",' +
            '  "name_mtz"  : "' + morda_mtz               + '",' +
            '  "name_map"  : "' + morda_map               + '",' +
            '  "name_dmap" : "' + morda_dmap              + '",' +
            '  "sge_q"     : "' + self.queueName          + '",' +
            '  "sge_tc"    : "' + str(self.nSubJobs)      + '",' +
            '  "subjobs"   : "subjobs" ' +
            '}'
        )

        # make command-line parameters for morda_sge.py
        cmd = [ "-m","morda",
                self.exeType,
                "-f",self.mtzpath,
                "-s",self.seqpath,
                "-d",self.rvapi_doc_path,
                #"-a",
                "-n","1"
              ]

        #if self.task.parameters.sec1.contains.NMODELS.value:
        #    cmd = cmd + [ "-n",str(self.task.parameters.sec1.contains.NMODELS.value) ]

        # run morda
        self.runApp ( "ccp4-python",cmd )

        self.restoreReportDocument()

        #  MoRDa puts final files in "output" directory, so update our paths
        morda_xyz  = os.path.join ( self.outputdir,morda_xyz )
        morda_mtz  = os.path.join ( self.outputdir,morda_mtz )
        morda_map  = os.path.join ( self.outputdir,morda_map )
        morda_dmap = os.path.join ( self.outputdir,morda_dmap )

        # check for solution
        nResults = 0
        rfree    = 1.0
        if os.path.isfile(morda_xyz):
            nResults = 1
            f = open ( os.path.join(self.outputdir,"morda.res") )
            flines = f.readlines()
            f.close()
            rfree = float(flines[1])

        quit_message = self.saveResults ( self.morda_dir(),nResults,rfree,
                                    morda_xyz,morda_mtz,morda_map,morda_dmap )

        self.quit_branch ( branch_data,"Automated Molecular Replacement (MoRDa): " +
                                       quit_message )

        return self.morda_header_id()
